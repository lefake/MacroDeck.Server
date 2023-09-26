import webbrowser
from subprocess import Popen

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

class VMActions:
    def __init__(self, vm):
        self.vm = vm
    def set_strip_gain(self, id, value: float):
        self.vm.strip[id].gain = value

    def set_strip_mute(self, id, value):
        self.vm.strip[id].mute = value

    def toggle_strip_mute(self, id):
        self.vm.strip[id].mute = not self.vm.strip[id].mute

    def set_bus_gain(self, id, value):
        self.vm.bus[id].gain = value

    def set_bus_mute(self, id, value):
        self.vm.bus[id].mute = value

    def set_app_gain(self, id, name, value):
        self.vm.strip[id].appgain(name, value)

    def set_app_mute(self, id, name, value):
        self.vm.strip[id].appmute(name, value)

    def set_a1(self, id, value):
        self.vm.strip[id].A1 = value

    def set_a2(self, id, value):
        self.vm.strip[id].A2 = value

    def set_a3(self, id, value):
        self.vm.strip[id].A3 = value

    def set_a4(self, id, value):
        self.vm.strip[id].A4 = value

    def set_a5(self, id, value):
        self.vm.strip[id].A5 = value

    def set_b1(self, id, value):
        self.vm.strip[id].B1 = value

    def set_b2(self, id, value):
        self.vm.strip[id].B2 = value

    def set_b3(self, id, value):
        self.vm.strip[id].B3 = value

    def get_strip_level(self, id):
        return self.vm.strip[id].levels.postfader
    # TODO : Add levels if needed

    def get_strip_gain(self, id):
        return self.vm.strip[id].gain
    def is_strip_muted(self, id):
        return int(self.vm.strip[id].mute)

    def get_a1(self, id):
        return self.vm.strip[id].A1

    def get_a2(self, id):
        return self.vm.strip[id].A2

    def get_a3(self, id):
        return self.vm.strip[id].A3

    def get_a4(self, id):
        return self.vm.strip[id].A4

    def get_a5(self, id):
        return self.vm.strip[id].A5

    def get_b1(self, id):
        return self.vm.strip[id].B1

    def get_b2(self, id):
        return self.vm.strip[id].B2

    def get_b3(self, id):
        return self.vm.strip[id].B3

class WindowsActions:
    def __init__(self):
        self.processes = {}
    @staticmethod
    def open_new(url):
        webbrowser.open_new(url)

    @staticmethod
    def open_new_tab(url):
        webbrowser.open_new_tab(url)

    def open_app(self, name):
        self.processes[name] = Popen([app_dict[name]])

    def close_app(self, name):
        self.processes[name].terminate()