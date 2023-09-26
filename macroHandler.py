from constants import *

class MacroHandler:
    def __init__(self, vActions, wActions):
        self.vmActions = vActions
        self.wActions = wActions

        self.macro_states = [0 for _ in range(len(MAP_HW_MACRO))]
        self.macro_saved_states = [{} for _ in range(len(MAP_HW_MACRO))]
        self.macros = [self.macro0,
                       self.macro1,
                       self.macro2,
                       self.macro3,
                       self.macro4,
                       self.macro5,
                       self.macro6,
                       self.macro6]

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
            self.wActions.open_app("Osu")
        else:
            self.vmActions.set_strip_mute(MUSIC_ID, self.macro_saved_states[0]["m_mute"])
            self.vmActions.set_strip_mute(GAMES_ID, self.macro_saved_states[0]["g_mute"])
            self.vmActions.set_strip_gain(GAMES_ID, self.macro_saved_states[0]["g_gain"])
            self.vmActions.set_b2(GAMES_ID, self.macro_saved_states[0]["g_a2"])
            self.wActions.close_app("Osu")

    def macro1(self):
        pass

    def macro2(self):
        pass

    def macro3(self):
        pass

    def macro4(self):
        pass

    def macro5(self):
        pass

    def macro6(self):
        pass

    def macro7(self):
        pass
