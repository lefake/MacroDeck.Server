import voicemeeterlib
from flask import Flask, request, make_response
from flask_api import status

from VM.Linker import Linker

app = Flask(__name__, static_folder='.')

BAD_ARGS = ("Record not found", status.HTTP_400_BAD_REQUEST)

def valid_response(content):
    res = make_response(str(content), status.HTTP_200_OK)
    res.mimetype = "text/plain"
    return res



@app.route('/is_strip_muted', methods=['GET'])
def is_strip_muted():
    args = request.args

    if 's' in args.keys():
        muted = linker.is_strip_muted(int(args.get('s')))
        return valid_response(muted)
    else:
        return BAD_ARGS

@app.route('/are_strips_muted', methods=['GET'])
def are_strips_muted():
    body = ""
    for i in range(8):
        body += str(linker.is_strip_muted(i)) + ','

    return valid_response(body[:-1])

@app.route('/mute_strip', methods=['POST'])
def mute_strip():
    args = request.args

    if 's' in args.keys():
        linker.toggle_mute_strip(int(args.get('s')))
        return valid_response("OK")
    else:
        return BAD_ARGS



@app.route('/push_strip', methods=['POST'])
def push_strip():
    args = request.args

    if 's' in args.keys():
        if 'g' in args.keys():
            linker.set_gain(int(args.get('s')), float(args.get('g')))

        if 'm' in args.keys():
            linker.toggle_mute_strip(int(args.get('s')))

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
        return valid_response(linker.is_strip_muted(int(args.get('s'))))








# @app.route('/macro', methods=['GET'])
# def macro():
#     args = request.args
#
#     if args.get('m'):
#         return {args.get('m'): False}
#     else:
#         return "Record not found", status.HTTP_400_BAD_REQUEST

# @app.route('/volume', methods=['GET'])
# def volume():
#     args = request.args
#
#     if 's' in args.keys():
#         lvls = linker.get_gain(int(args.get('s')))
#         return {'l': lvls[0], 'r': lvls[1]}
#     else:
#         return BAD_ARGS
#
# @app.route('/set_gain', methods=['POST'])
# def set_gain():
#     args = request.args
#
#     if 's' in args.keys() and 'v' in args.keys():
#         linker.set_gain(int(args.get('s')), float(args.get('v')))
#         return "OK", status.HTTP_200_OK
#     else:
#         return BAD_ARGS

@app.route('/')
def main():
    return app.send_static_file("bob.html")

if __name__ == "__main__":
    with voicemeeterlib.api("potato") as vm:
        linker = Linker(vm)
        app.run(host='192.168.2.13', port=5000)