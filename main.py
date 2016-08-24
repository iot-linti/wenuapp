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
#gesture
#import gesture_box as gesture
from kivy.uix.boxlayout import BoxLayout

#import requests
import json
import os
import datetime
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
		self.ids['fecha'].text += datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y %H:%M')

		self.screens = ['info','historial']

		Logger.info('info: iniciando')
		self.list_of_prev_screens = []
		self.valores = {'False':'Falso', 'True':'Verdadero' }
		self.etiquetas_coc = ['current_coc', 'motion_coc', 'mote_id_coc', 'temperature_coc', 'time_coc']
		self.etiquetas_control = ['current', 'motion', 'mote_id', 'temperature', 'time']
		self.sensores = ['linti_cocina','linti_oficina_1','linti_control','linti_servidores']


	def calcular_color(self, val):
		#temp_ambiental = requests.get('http://clima.info.unlp.edu.ar/last')
		#~ print temp_ambiental.status_code
		#~ print temp_ambiental.headers['content-type']
		#~ print ".......----------...................."
		#dict_temp_amb = json.loads(temp_ambiental.text)
		return "[color=f10000]"+str(val)+"[/color]" if val > self.temp_amb + 5 else "[color=13E400]"+str(val)+"[/color]"

	def procesar_datos_cocina(self, data):
		#datos sensor cocina
		datos =[]
		temp = self.calcular_color(data["temperature"])
		datos.append(str(temp))
		datos.append(str(data['time'].split(':')[0][:10]))
		return datos

	def obtener_temp_ambiente(self, data):
		pass

	def mostrar_historial(self):
		print "historial mota mapa"


	def actualizar(self):
		try:
			query = 'SELECT * as temperatura FROM climatizacion ORDER BY time desc LIMIT '+self.ids["cantidad_fin"].text+' OFFSET '+self.ids["cantidad_ini"].text
			print query
			res = self.client.query(query) #Consulta meramente de prueba
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
					temp_color = self.calcular_color(r["temperature"]) #"[color=f10000]"+str(r["temperature"])+"[/color]" if r["temperature"] > dict_temp_amb["temperature"] + 5 else "[color=ffffff]"+str(r["temperature"])+"[/color]"

					self.ids["grid_filter"].add_widget(Label(text=temp_color, markup= True))
					self.ids["grid_filter"].add_widget(Label(text=str(r["current"])))
					self.ids["grid_filter"].add_widget(Label(text=str(r["time"])))
					self.ids["grid_filter"].add_widget(Label(text=r["mote_id"]))
					self.ids["grid_filter"].add_widget(Label(text=str(r["motion"])))

				#~ self.ids["grid_filter"].add_widget(self.line)

	def actualizar_mapa(self):
		try:
			#~ query = []
			query = {}
			for s in self.sensores:
				#~ print s
				#~ query.append("SELECT * as temperatura FROM climatizacion WHERE mote_id = '"+s+"' ORDER BY time desc LIMIT 1")
				query[s] = "SELECT * as temperatura FROM climatizacion WHERE mote_id = '"+s+"' ORDER BY time desc LIMIT 1"
			res = {}
			for q in query.items():
				print "---------------------------------------------------------------------------------------------------------"
				print q[0]
				print q[1]
				#~ res.append(self.client.query(q)) #Consulta meramente de prueba
				res[q[0]] = self.client.query(q[1]).items()[0][1].next() #Consulta meramente de prueba
			try:
				self.temp_amb = res['linti_control']['temperature']#[0][('climatizacion', None)].next()['temperature']
			except:
				print "asdkmaskdnkasndasmd---------------------------------------------------------------"
				#~ print res['linti_control'][0].next()
		except Exception, e:
			print("Error al efectuar la consulta 1 "+str(e))
		else:
			#~ self.temp_amb = res['linti_control']['temperature']#[('climatizacion', None)].next()['temperature']
			for s in self.sensores:
				temp_color = self.calcular_color(res[s]['temperature'])
				self.ids[s].text = temp_color
				self.ids[s].texture_update()
			self.ids['fecha'].text = 'Ultima actualización: '+datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y %H:%M')

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
		self.actualizar_mapa()
		#~ self.ids["pannel_tab"].bind(current_tab=self.update_content)
		self.actualizar()

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
