from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, ListProperty, NumericProperty, ReferenceListProperty
from kivy.core.window import Window as win
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.clock import Clock
import os

class Info(FloatLayout):

    try:
        screen_manager = ObjectProperty(None)
    except Exception:
        Logger.exception('Info: NO se pudo iniciar')

    def __init__(self, *args, **kwargs):
        super(Info, self).__init__(**kwargs)
        self.icon = 'pin_1.png'
        self.title = 'Datos Sensores'

        Logger.info('info: iniciando')
        self.list_of_prev_screens = []


    def actualizar(self):
        pass

    def iniciar(self, actual_screen, next_screen):
        Logger.info('datos: cambio pantalla')
        #if next_screen == "info":
            #Clock.schedule_interval(self.update, 0.5)

        self.onNextScreen(actual_screen, next_screen)

    def onBackBtn(self):
        # Check if there are any screens to go back to
        if self.list_of_prev_screens:
            # If there are then just go back to it
            self.screen_manager.current = self.list_of_prev_screens.pop()
            print(self.screen_manager.current)
            # We don't want to close app
            return True
        # No more screens so user must want to exit app
        return False

    def onNextScreen(self, actual_screen, next_screen):
        # add screen we were just in
        self.list_of_prev_screens.append(actual_screen.name)
        # Go to next screen
        self.screen_manager.current = next_screen


################################################################################

class DatosApp(App):
    """ App to show how to use back button """

    def __init__(self, *args, **kwargs):
        super(DatosApp, self).__init__(*args, **kwargs)
        win.bind(on_keyboard=self.onBackBtn)

    def onBackBtn(self, window, key, *args):
        """ To be called whenever user presses Back/Esc Key """
        # If user presses Back/Esc Key
        if key == 27:
            return self.root.onBackBtn()
        return False

    def build(self):
        j = Info()
        return j


if __name__ == "__main__":
    DatosApp().run()
