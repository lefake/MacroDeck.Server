from VM.actions import BaseActions, Macros


class Linker:
    def __init__(self, vm):
        self._actions = BaseActions(vm)
        self._macros = Macros(self._actions)

        self._map = [self._macros.osu_off,
                     self._macros.open_twitch,
                     self._macros.osu_off,
                     self._macros.osu_off,
                     self._macros.osu_off,
                     self._macros.osu_off,
                     self._macros.osu_off,
                     self._macros.osu_off]

        # TODO : Get all toggle value loaded once

    def get_gain(self, strip_id):
        return self._actions.get_strip_level(strip_id)

    def set_gain(self, strip_id: int, value: float):
        self._actions.set_strip_gain(strip_id, value)

    def get_macro(self, macro_id):
        pass

    def mute_strip(self, strip_id: int, value: bool):
        self._actions.set_strip_mute(strip_id, value)

    def toggle_mute_strip(self, strip_id: int):
        self._actions.toggle_strip_mute(strip_id)

    def is_strip_muted(self, strip_id: int) -> bool:
        return self._actions.is_strip_muted(strip_id)

    def gain_cb(self, input):
        parsed = input.decode()[1:-1].split(";")[:-1]
        self._macros.apply_all_gains(parsed)

    def macro_cb(self, input):
        parsed = input.decode()[1:-1].split(";")[:-1]
        for i, b in enumerate(parsed):
            if b:
                self._map[i]()