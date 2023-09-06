import voicemeeterlib
import serial

from serial.SerialHandler import SerialHandler

if __name__ == "__main__":
    with voicemeeterlib.api("potato") as vm:
        linker = Linker(vm)

        arduino = serial.Serial('COM7', 9600, timeout=0.05),
        handler = SerialHandler(arduino, linker.gain_cb, linker.macro_cb)
        handler.run()


