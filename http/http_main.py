import voicemeeterlib
from flask import Flask, request
from flask_api import status

from VM.Linker import Linker

app = Flask(__name__, static_folder='.')

@app.route('/mute_strip', methods=['POST'])
def mute_strip():
    args = request.args

    if 's' in args.keys() and 'v' in args.keys():
        linker.mute_strip(int(args.get('s')), args.get('v') == 'True')
        return "OK", status.HTTP_200_OK
    else:
        return "Record not found", status.HTTP_400_BAD_REQUEST

@app.route('/macro', methods=['GET'])
def macro():
    args = request.args

    if args.get('m'):
        return {args.get('m'): False}
    else:
        return "Record not found", status.HTTP_400_BAD_REQUEST

@app.route('/volume', methods=['GET'])
def volume():
    args = request.args

    if 's' in args.keys():
        lvls = linker.get_gain(int(args.get('s')))
        return {'l': lvls[0], 'r': lvls[1]}
    else:
        return "Record not found", status.HTTP_400_BAD_REQUEST

@app.route('/set_gain', methods=['POST'])
def set_gain():
    args = request.args

    if 's' in args.keys() and 'v' in args.keys():
        linker.set_gain(int(args.get('s')), float(args.get('v')))
        return "OK", status.HTTP_200_OK
    else:
        return "Record not found", status.HTTP_400_BAD_REQUEST

@app.route('/')
def main():
    return app.send_static_file("bob.html")

if __name__ == "__main__":
    with voicemeeterlib.api("potato") as vm:
        linker = Linker(vm)
        app.run(host='192.168.2.13', port=5000)