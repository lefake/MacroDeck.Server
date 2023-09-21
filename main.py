import voicemeeterlib
from flask import Flask, request, make_response
from flask_api import status

BAD_ARGS = ("Record not found", status.HTTP_400_BAD_REQUEST)

app = Flask(__name__, static_folder='.')
vm = None

MOTORIZED = False

MAP_HW_VM = [0, 2]

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

        if len(gains) != len(MAP_HW_VM):
            return BAD_ARGS

        for i, vId in enumerate(MAP_HW_VM):
            vm.strip[vId].gain = float(gains[i])

    if 'm' in args.keys():
        mute = int(args.get('m'))
        bins = f'{mute:0{len(MAP_HW_VM)}b}'[::-1]
        for i, vId in enumerate(MAP_HW_VM):
            if bins[i] == "1":
                vm.strip[vId].mute = not vm.strip[vId].mute

    return valid_response("")

if __name__ == "__main__":
    with voicemeeterlib.api("potato") as VM:
        vm = VM
        vm.vm_pdirty()
        app.run(host='192.168.2.13', port=5000)