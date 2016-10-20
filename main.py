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
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.core.text import Label as CoreLabel
from kivy.uix.popup import Popup
from kivy.utils import platform

#gesture
#import gesture_box as gesture
from kivy.uix.boxlayout import BoxLayout

#import requests
import json
import os
import datetime
from functools import partial
import urllib
#influx
from influxdb import InfluxDBClient


#nuestros modulos
from piso import Piso
class Info(FloatLayout):

	try:
		screen_manager = ObjectProperty(None)
	except Exception:
		Logger.exception('Info: NO se pudo iniciar')

	def __init__(self, *args, **kwargs):
		super(Info, self).__init__(**kwargs)
		self.icon = 'pin_1.png'
		self.title = 'Datos Sensores'
		#self.ids['fecha'].text += datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y %H:%M')

		self.screens = ['info','historial']

		Logger.info('info: iniciando')
		self.list_of_prev_screens = []
		self.valores = {'False':'Falso', 'True':'Verdadero' }


	def actualizar(self):
		try:
			query = 'SELECT * as temperatura FROM medicion ORDER BY time desc LIMIT '+self.ids["cantidad_fin"].text+' OFFSET '+self.ids["cantidad_ini"].text
			print query
			res = self.client.query(query)
		except Exception as e:
			print("Error al efectuar la consulta actualziar " + str(e.message))
		else:
			if len(self.ids["grid_filter"].children) > 5:
				for w in range(len(self.ids["grid_filter"].children) - 5):
					self.ids["grid_filter"].remove_widget(self.ids["grid_filter"].children[0])
			for re in res:
				self.ids["grid_filter"].bind(minimum_height=self.ids["grid_filter"].setter('height'))
				for r in re:
					#~ print r
					temp_color = self.calcular_color(r["temperatura"]) #"[color=f10000]"+str(r["temperature"])+"[/color]" if r["temperature"] > dict_temp_amb["temperature"] + 5 else "[color=ffffff]"+str(r["temperature"])+"[/color]"

					self.ids["grid_filter"].add_widget(Label(text=temp_color, markup= True))
					self.ids["grid_filter"].add_widget(Label(text=str(r["current"])))
					self.ids["grid_filter"].add_widget(Label(text=str(r["time"])))
					self.ids["grid_filter"].add_widget(Label(text=r["mota_id"]))
					self.ids["grid_filter"].add_widget(Label(text=str(r["motion"])))

				#~ self.ids["grid_filter"].add_widget(self.line)


	def iniciar(self, actual_screen, next_screen):
		Logger.info('datos: cambio pantalla')
		#if next_screen == "info":
			#Clock.schedule_interval(self.update, 0.5)
		try:
			self.client = InfluxDBClient('influxdb.linti.unlp.edu.ar', 8086, self.ids["usuario"].text, self.ids['password'].text, 'uso_racional')
			self.client.query('SELECT mota_id FROM medicion LIMIT 1') #por ahora la unica forma de testear la conexion.

		except:
			print("Error al efectuar la conexion")
			popup = Popup(title='Error al conectarse', content=Label(text="Error de conexión.\nVerifique su conexión a internet y sus credenciales de acceso.\n\n\nPara cerrar el cuadro de diálogo presione fuera de este."), size_hint=(.8, .6))
			popup.open()
		else:
			#instancio piso y paso el client - falta ahcer una consulta para saber cuantos pisos hay
			#~ pisos = ["1","2"]
			#~ pisos = [1,2]
			pisos = self.client.query('SELECT * FROM piso')
			print pisos.get_points().next()
			print "----------------------aaaaaaaaaaaaaaaaaaaa-------------------------------------"
			#p_imgs = ["imagenes/plano-2piso.jpg","imagenes/primer_piso.jpg"]
			self.pisos = []
			#~ self.spinner = Spinner(text="1", size_hint= (.09,.05), pos_hint={'top':1,'left':.9})
			for pp in pisos:
				for p in pp:
					print "*************************************"
					print p
					print "**********************pppppp*********"
					#~ self.spinner.values.append(str(p))
					sensores = self.client.query("SELECT * FROM mota WHERE piso_id ='"+str(p["piso_id"])+"'")
					print sensores
					print "+++++++++++++++++++++++++****++++++++++++++++++++++++++++++"
					img = 'piso_'+str(p["piso_id"])+'.png'
					print img
					if ((not os.path.exists(img)) and (not os.path.exists("imagenes/"+img))):
						try:
							urllib.urlretrieve(str(p['mapa']),img)
						except Exception as e:
							print "Error al descargar la imagen del piso"+img+"\n"
							print e
					#~ else:
					self.pisos.append(Piso(p['piso_id'], sensores, img, self.client, pisos))
					self.pisos[-1].agregar_motas()
					self.screen_manager.add_widget(self.pisos[-1])
			else:
				self.screen_manager.current = next_screen
		#~ self.actualizar_mapa()
		#~ self.ids["pannel_tab"].bind(current_tab=self.update_content)
		#~ self.actualizar()

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

    def on_pause(self):
        if platform == 'android':
            from android import AndroidService
            service = AndroidService('Datos Sensores', 'running')
            service.start('service started')
            self.service = service
        return True
            #~ #~
    def on_resume(self):
		self.service.stop()
		self.service = None


if __name__ == "__main__":
    DatosApp().run()
