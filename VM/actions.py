import webbrowser
from subprocess import Popen

# VM constants
MIC_ID = 0
MUSIC_ID = 1
DISCORD_ID = 2
FIREFOX_ID = 3
GAMES_ID = 5
GENERAL_ID = 7

class BaseActions:
    app_dict = {
        "KeePassXC": "C:\\Program Files\\KeePassXC\\KeePassXC.exe",
        "Firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
        "Discord": "C:\\Users\\lefake\\AppData\\Local\\Discord\\Update.exe --processStart Discord.exe",
        "Sonixd": "C:\\Users\\lefake\\AppData\\Local\\Programs\\Sonixd\\Sonixd.exe",
        "MobaXterm": "C:\\Program Files (x86)\\Mobatek\\MobaXterm\\MobaXterm.exe",
        "WaveForms": "C:\\Program Files (x86)\\Digilent\\WaveForms3\\WaveForms.exe",
        "Arduino": "C:\\Users\\lefake\\AppData\\Local\\Programs\\Arduino IDE\\Arduino IDE.exe",
        "Osu": "C:\\Users\\lefake\\AppData\\Local\\osu!\\osu!.exe",
        "IntelliJ": "C:\\Program Files\\JetBrains\\IntelliJ IDEA Community Edition 2022.2.1\\bin\\idea64.exe",
        "PyCharm": "C:\\Program Files\\JetBrains\\PyCharm Community Edition 2022.2.1\\bin\\pycharm64.exe",
        "Clion": "C:\\Program Files\\JetBrains\\CLion 2022.2.4\\bin\\clion64.exe",
        "DockerDesktop": "C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe",
    }

    def __init__(self, vm):
        self._vm = vm

    # VM functions

    def set_strip_gain(self, id, value: float):
        self._vm.strip[id].gain = value

    def set_strip_mute(self, id, value):
        self._vm.strip[id].mute = value

    def set_bus_gain(self, id, value):
        self._vm.bus[id].gain = value

    def set_bus_mute(self, id, value):
        self._vm.bus[id].mute = value

    def set_app_gain(self, id, name, value):
        self._vm.strip[id].appgain(name, value)

    def set_app_mute(self, id, name, value):
        self._vm.strip[id].appmute(name, value)

    def set_a1(self, id, value):
        self._vm.strip[id].A1 = value

    def set_a2(self, id, value):
        self._vm.strip[id].A2 = value

    def set_a3(self, id, value):
        self._vm.strip[id].A3 = value

    def set_a4(self, id, value):
        self._vm.strip[id].A4 = value

    def set_a5(self, id, value):
        self._vm.strip[id].A5 = value

    def set_b1(self, id, value):
        self._vm.strip[id].B1 = value

    def set_b2(self, id, value):
        self._vm.strip[id].B2 = value

    def set_b3(self, id, value):
        self._vm.strip[id].B3 = value

    def get_strip_level(self, id):
        return self._vm.strip[id].levels.postfader
    # TODO : Add levels if needed

    # Browser functions

    def open_new(self, url):
        webbrowser.open_new(url)

    def open_new_tab(self, url):
        webbrowser.open_new_tab(url)

    # App functions

    def open_app(self, name):
        Popen([self.app_dict[name]])

class Macros:
    def __init__(self, base_action):
        self._base_actions = base_action

    def apply_all_gains(self, values):
        for i, v in enumerate(values):
            self._base_actions.set_strip_gain(i, int(v))

    def osu_on(self):
        self._base_actions.open_app("Osu")
        self._base_actions.set_strip_mute(1, True)
        self._base_actions.set_strip_mute(5, False)
        self._base_actions.set_strip_gain(5, -4.0)
        self._base_actions.set_b2(5, True)

    def osu_off(self):
        self._base_actions.set_strip_mute(1, False)
        self._base_actions.set_strip_mute(5, True)
        self._base_actions.set_b2(5, False)

    def open_twitch(self, streamer=""):
        self._base_actions.open_new_tab("www.twitch.tv/" + streamer)