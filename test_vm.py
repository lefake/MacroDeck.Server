import threading
from time import sleep

import voicemeeterlib

run = True

def look(vm):
    while run:
        if vm.pdirty:
            print("Dirty")

if __name__ == "__main__":
    with voicemeeterlib.api("potato") as vm:
        t = threading.Thread(target=look, args=(vm,))
        t.start()
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            run = False
            t.join()
