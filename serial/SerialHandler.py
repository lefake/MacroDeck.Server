import threading
import time

class SerialHandler(threading.Thread):
    def __init__(self, serial, gain_cb, macro_cb, sleeptime=0.01):
        threading.Thread.__init__(self)

        self._serial = serial[0]
        self._gain_cb = gain_cb
        self._macro_cb = macro_cb
        self._sleeptime = sleeptime

        self._response = None
        self._run = False

    def run(self):
        self._run = True
        self.worker()

    def kill(self):
        self._run = False

    def worker(self):
        while self._run:
            try:
                if self._serial.in_waiting > 0:
                    try:
                        input = self._serial.read()

                        if input == b'<':
                            buffer = self._serial.read_until(b'>')
                            self._serial.flush()
                            self._response = b'<' + buffer
                            self._gain_cb(self._response)

                        elif input == b'{':
                            buffer = self._serial.read_until(b'}')
                            self._serial.flush()
                            self._response = b'{' + buffer
                            self._macro_cb(self._response)

                    except Exception as e:
                        print("Read call back error " + str(e)) # TODO : Add file logger

                time.sleep(self._sleeptime)
            except Exception as e:
                print("Read error " + str(e))