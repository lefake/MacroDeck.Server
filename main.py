import threading
import time

import voicemeeterlib

from actions import VMActions, WindowsActions
from constants import MAP_HW_VM, MAP_HW_MACRO
from macroHandler import MacroHandler
from MQTTServer import MQTTServer

running = True

def str_to_bin(msg: str, l: int) -> str:
    mute = int(msg)
    return f'{mute:0{l}b}'[::-1]

def gains_cb(msg: str):
    parts = msg.split(':')
    vmActions.set_strip_gain(MAP_HW_VM[int(parts[0])], float(parts[1]))

def mutes_cb(msg: str):
    bins = str_to_bin(msg, len(MAP_HW_VM))

    for i, vId in enumerate(MAP_HW_VM):
        if bins[i] == "1":
            vmActions.toggle_strip_mute(vId)

def macros_cb(msg: str):
    bins = str_to_bin(msg, len(MAP_HW_MACRO))

    for i, mId in enumerate(MAP_HW_MACRO):
        if bins[i] == "1":
            macro.toggle_macro(mId)

def push_vm_state(vm, pub_cb):
    current_mutes = []
    for i, s in enumerate(MAP_HW_VM):
        current_mutes.append(vm.strip[s].mute)

    vm.clear_dirty()

    while running:
        mutes = []
        for i, s in enumerate(MAP_HW_VM):
            mutes.append(vm.strip[s].mute)

        if mutes != current_mutes:
            current_mutes = mutes
            mute = ''.join(['1' if x else '0' for x in current_mutes])
            pub_cb("macrodeck/vm", str(int(mute[::-1], 2)))
            vm.clear_dirty()

        time.sleep(0.1)

if __name__ == "__main__":
    subs = {"macrodeck/gains": gains_cb,
              "macrodeck/mutes": mutes_cb,
              "macrodeck/macros": macros_cb}

    with voicemeeterlib.api("potato") as vm:
        vmActions = VMActions(vm)
        wActions = WindowsActions()
        macro = MacroHandler(vmActions, wActions)

        mqtt = MQTTServer("192.168.2.128", subs)
        mqtt.start()

        t = threading.Thread(target=push_vm_state, args=(vm, mqtt.publish))
        t.start()

        try:
            while True:
                mqtt.publish("macrodeck/hb", str(1))
                time.sleep(1)
        except KeyboardInterrupt:
            mqtt.stop()
            running = False
            t.join(timeout=1)
