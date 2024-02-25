from typing import Any

from constants import *

class MacroHandler:
    def __init__(self, vActions, wActions):
        self.vmActions = vActions
        self.wActions = wActions

        self.macro_states = [0 for _ in range(len(MAP_HW_MACRO))]
        self.macro_saved_states: list[dict[str, Any]] = [{} for _ in range(len(MAP_HW_MACRO))]
        self.macros = [self.macro0,
                       self.macro1,
                       self.macro2,
                       self.macro3,
                       self.macro4,
                       self.macro5,]

    def toggle_macro(self, mId):
        self.macros[mId](not self.macro_states[mId])
        self.macro_states[mId] = not self.macro_states[mId]

    def macro0(self, state):
        if state:
            self.macro_saved_states[0] = {
                "m_mute": self.vmActions.is_strip_muted(MUSIC_ID),
                "g_mute": self.vmActions.is_strip_muted(GAMES_ID),
                "g_gain": self.vmActions.get_strip_gain(GAMES_ID),
                "g_a2": self.vmActions.get_a2(GAMES_ID)
            }

            self.vmActions.set_strip_mute(MUSIC_ID, 1)
            self.vmActions.set_strip_mute(GAMES_ID, 0)
            self.vmActions.set_strip_gain(GAMES_ID, -4.0)
            self.vmActions.set_b2(GAMES_ID, 1)
            # self.wActions.open_app("Osu")
        else:
            self.vmActions.set_strip_mute(MUSIC_ID, self.macro_saved_states[0]["m_mute"])
            self.vmActions.set_strip_mute(GAMES_ID, self.macro_saved_states[0]["g_mute"])
            self.vmActions.set_strip_gain(GAMES_ID, self.macro_saved_states[0]["g_gain"])
            self.vmActions.set_b2(GAMES_ID, self.macro_saved_states[0]["g_a2"])
            # self.wActions.close_app("Osu")

    def macro1(self, state):
        if state:
            self.macro_saved_states[1] = {
                "m_a2": self.vmActions.get_a2(MUSIC_ID),
                "d_a2": self.vmActions.get_a2(DISCORD_ID),
                "f_a2": self.vmActions.get_a2(FIREFOX_ID),
                "g_a2": self.vmActions.get_a2(GAMES_ID),
                "ge_a2": self.vmActions.get_a2(GENERAL_ID)
            }

            self.vmActions.set_a2(MUSIC_ID, True)
            self.vmActions.set_a2(DISCORD_ID, True)
            self.vmActions.set_a2(FIREFOX_ID, True)
            self.vmActions.set_a2(GAMES_ID, True)
            self.vmActions.set_a2(GENERAL_ID, True)

            self.vmActions.set_bus_mute(G533_ID, True)
            self.vmActions.set_bus_mute(SPEAKER_ID, False)
        else:
            self.vmActions.set_a2(MUSIC_ID, self.macro_saved_states[1]["m_a2"])
            self.vmActions.set_a2(DISCORD_ID, self.macro_saved_states[1]["d_a2"])
            self.vmActions.set_a2(FIREFOX_ID, self.macro_saved_states[1]["f_a2"])
            self.vmActions.set_a2(GAMES_ID, self.macro_saved_states[1]["g_a2"])
            self.vmActions.set_a2(GENERAL_ID, self.macro_saved_states[1]["ge_a2"])

            self.vmActions.set_bus_mute(G533_ID, False)
            self.vmActions.set_bus_mute(SPEAKER_ID, True)

    def macro2(self, state):
        if state:
            self.wActions.open_app("Discord")
            self.wActions.open_app("Sonixd")
            self.wActions.open_app("PyCharm")
            self.wActions.open_app("Clion")
            self.wActions.open_app("VSCode")
            self.wActions.open_app("Firefox")
            self.wActions.open_new("https://www.twitch.tv")
            self.wActions.open_new("https://chat.openai.com/")
        else:
            self.wActions.close_app("Clion")
            self.wActions.close_app("VSCode")

    def macro3(self, state):
        pass

    def macro4(self, state):
        pass

    def macro5(self, _):
        self.vmActions.restart_engine()
