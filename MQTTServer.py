from typing import Callable, Any

import paho.mqtt.client as mqtt

class MQTTServer:
    def __init__(self, ip: str, sub_callbacks: dict[str, Callable[[str], None]]):
        self.ip: str = ip
        self.sub_cb: dict[str, Callable[[str], None]] = sub_callbacks

        self.mqtt = mqtt.Client("MacroDeckServer")
        self.mqtt.on_message = self.__msg_in__
        self.mqtt.on_connect = self.__on_connect__

        self.connected = False

    def start(self):
        self.mqtt.connect(self.ip)
        self.mqtt.loop_start()

    def stop(self):
        self.mqtt.loop_stop()
        self.mqtt.disconnect()

    def publish(self, topic: str, msg: Any):
        self.mqtt.publish(topic, msg)

    def __msg_in__(self, client, userdata, message):
        if message.topic in self.sub_cb:
            self.sub_cb[message.topic](message.payload.decode())

    def __on_connect__(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            for t in self.sub_cb.keys():
                self.mqtt.subscribe(t)