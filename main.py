import voicemeeterlib
from flask import Flask, request, make_response
from flask_api import status

from macroHandler import MacroHandler
from actions import VMActions, WindowsActions
from constants import *

BAD_ARGS = ("Record not found", status.HTTP_400_BAD_REQUEST)

app = Flask(__name__, static_folder='.')
vmActions = None
macro = None


def valid_response(content):
    res = make_response(str(content), status.HTTP_200_OK)
    res.mimetype = "text/plain"
    return res

@app.route('/pull', methods=['GET'])
def pull():
    if any(request.args.keys()):
        return BAD_ARGS

    mute = ""
    gain = ""

    for vId in MAP_HW_VM:
        if MOTORIZED:
            gain += str(vmActions.get_strip_gain(vId)) + ','
        mute += '1' if vmActions.is_strip_muted(vId) else '0'

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
            vmActions.set_strip_gain(MAP_HW_VM[int(vId)], float(g))

    if 'm' in args.keys():
        mute = int(args.get('m'))
        bins = f'{mute:0{len(MAP_HW_VM)}b}'[::-1]

        if len(bins) != len(MAP_HW_VM):
            return BAD_ARGS

        for i, vId in enumerate(MAP_HW_VM):
            if bins[i] == "1":
                vmActions.toggle_strip_mute(vId)

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
                macro.toggle_macro(mId)

    return valid_response("")

if __name__ == "__main__":
    with voicemeeterlib.api("potato") as vm:
        vmActions = VMActions(vm)
        wActions = WindowsActions()
        macro = MacroHandler(vmActions, wActions)
        app.run(host='192.168.2.13', port=5000)