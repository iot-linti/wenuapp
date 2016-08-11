#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, ListProperty, NumericProperty, ReferenceListProperty
from kivy.core.window import Window as win
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
import os
#influx
from influxdb import InfluxDBClient

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
		#~ print self.ids
		try:
			query = 'SELECT * as temperatura FROM climatizacion ORDER BY time asc LIMIT '+self.ids["cantidad_fin"].text+' OFFSET '+self.ids["cantidad_ini"].text
			print query
			res = self.client.query(query) #Consulta meramente de prueba
		except:
			print("Error al efectuar la consulta")
		else:
			print "--------------------------"
			#~ print res
			self.ids["scroll_grid"].clear_widgets()
			for re in res:
				print "............."
				line = GridLayout(cols=5, spacing=30)
				line.bind(minimum_height=line.setter('height'))
				for r in re:
					#~ print r
					line.add_widget(Label(text=str(r["temperature"])))
					line.add_widget(Label(text=str(r["current"])))
					line.add_widget(Label(text=str(r["time"])))
					line.add_widget(Label(text=r["mote_id"]))
					line.add_widget(Label(text=str(r["motion"])))
				self.ids["scroll_grid"].add_widget(line)

    def iniciar(self, actual_screen, next_screen):
        Logger.info('datos: cambio pantalla')
        #if next_screen == "info":
            #Clock.schedule_interval(self.update, 0.5)
        try:
			self.client = InfluxDBClient('influxdb.linti.unlp.edu.ar', 8086, self.ids["usuario"].text, self.ids['password'].text, 'uso_racional')
			self.client.query('SELECT mote_id FROM climatizacion LIMIT 1') #por ahora la unica forma de testear la conexion.
        except:
			print("Error al efectuar la conexion")
        else:
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
