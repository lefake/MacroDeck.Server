import voicemeeterlib
from flask import Flask, request, make_response
from flask_api import status

BAD_ARGS = ("Record not found", status.HTTP_400_BAD_REQUEST)

app = Flask(__name__, static_folder='.')
vm = None

MOTORIZED = False

MAP_HW_VM = [0, 1, 2, 4, 5]
MAP_HW_MACRO = [0, 1, 2, 3, 4, 5, 6, 7]

def valid_response(content):
    res = make_response(str(content), status.HTTP_200_OK)
    res.mimetype = "text/plain"
    return res

@app.route('/push_strip', methods=['POST'])
def push_strip():
    args = request.args

    if 's' in args.keys():
        if 'g' in args.keys():
            vm.strip[int(args.get('s'))].gain = float(args.get('g'))

        if 'm' in args.keys():
            vm.strip[int(args.get('s'))].mute = not vm.strip[int(args.get('s'))].mute

        if 'g' in args.keys() or 'm' in args.keys():
            return valid_response("OK")
        else:
            return BAD_ARGS
    else:
        return BAD_ARGS

@app.route('/pull_strip', methods=['GET'])
def pull_strip():
    args = request.args

    if 's' in args.keys():
        return valid_response(vm.strip[int(args.get('s'))].mute)

@app.route('/pull', methods=['GET'])
def pull():
    if any(request.args.keys()):
        return BAD_ARGS

    mute = ""
    gain = ""

    for vId in MAP_HW_VM:
        if MOTORIZED:
            gain += str(vm.strip[vId].gain) + ','
        mute += '1' if vm.strip[vId].mute else '0'

    return valid_response(gain + str(int(mute[::-1], 2)))

@app.route('/push', methods=['POST'])
def push():
    args = request.args

    if 'g' in args.keys():
        gains = args.get('g')[:-1].split(',')

        if len(gains) > len(MAP_HW_VM):
            return BAD_ARGS

        for pair in gains:
            vId, g = pair.split(':')
            vm.strip[MAP_HW_VM[int(vId)]].gain = float(g)

    if 'm' in args.keys():
        mute = int(args.get('m'))
        bins = f'{mute:0{len(MAP_HW_VM)}b}'[::-1]

        if len(bins) != len(MAP_HW_VM):
            return BAD_ARGS

        for i, vId in enumerate(MAP_HW_VM):
            if bins[i] == "1":
                vm.strip[vId].mute = not vm.strip[vId].mute

    return valid_response("")

@app.route('/pullMacro', methods=['GET'])
def pullMacro():
    return valid_response("")

@app.route('/pushMacro', methods=['POST'])
def pushMacro():
    args = request.args

    if 'm' in args.keys():
        macros = int(args.get('m'))
        bins = f'{macros:0{len(MAP_HW_MACRO)}b}'[::-1]

        if len(bins) != len(MAP_HW_MACRO):
            return BAD_ARGS

        for i, mId in enumerate(MAP_HW_MACRO):
            if bins[i] == "1":
                print(f"Macro {mId} toggled")

    return valid_response("")

if __name__ == "__main__":
    with voicemeeterlib.api("potato") as VM:
        vm = VM
        app.run(host='192.168.2.13', port=5000)