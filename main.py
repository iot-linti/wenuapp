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

#import requests
import json
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
		self.valores = {'False':'Falso', 'True':'Verdadero' }
		self.etiquetas_coc = ['current_coc', 'motion_coc', 'mote_id_coc', 'temperature_coc', 'time_coc']
		self.etiquetas_control = ['current', 'motion', 'mote_id', 'temperature', 'time']


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
		#~ datos.append(str(data['current']))
		#~ datos.append(self.valores[str(data['motion'])])
		#~ etiqueta = str(data['mote_id'].split('_')[0]).title() + ' ' + str(data['mote_id'].split('_')[1])
		#~ datos.append(etiqueta)
		temp = self.calcular_color(data["temperature"])
		datos.append(str(temp))
		datos.append(str(data['time'].split(':')[0][:10]))
		return datos
	
	def obtener_temp_ambiente(self, data):
		pass
		

	def actualizar(self):
		try:
			query = 'SELECT * as temperatura FROM climatizacion ORDER BY time desc LIMIT '+self.ids["cantidad_fin"].text+' OFFSET '+self.ids["cantidad_ini"].text
			print query
			res = self.client.query(query) #Consulta meramente de prueba
		except Eception as e:
			print("Error al efectuar la consulta actualziar " + e.message)
		else:
			print "--------------------------"
			print res
			self.ids["scroll_grid"].clear_widgets()
			for re in res:
				print "............."
				line = GridLayout(cols=5, spacing=30)
				line.bind(minimum_height=line.setter('height'))
				for r in re:
					#~ print r
					temp_color = self.calcular_color(r["temperature"]) #"[color=f10000]"+str(r["temperature"])+"[/color]" if r["temperature"] > dict_temp_amb["temperature"] + 5 else "[color=ffffff]"+str(r["temperature"])+"[/color]"

					line.add_widget(Label(text=temp_color, markup= True))
					line.add_widget(Label(text=str(r["current"])))
					line.add_widget(Label(text=str(r["time"])))
					line.add_widget(Label(text=r["mote_id"]))
					line.add_widget(Label(text=str(r["motion"])))

				self.ids["scroll_grid"].add_widget(line)

	def actualizar_mapa(self):
		print "aslllllllllllllllllllllllllllllllllllllllllllllllll"
		try:
			#~ query = 'SELECT * as temperatura FROM climatizacion GROUP BY mote_id ORDER BY time desc LIMIT 1'
			query = "SELECT * as temperatura FROM climatizacion WHERE mote_id = 'linti_cocina' ORDER BY time desc LIMIT 1"
			query2 = "SELECT * as temperatura FROM climatizacion WHERE mote_id = 'linti_oficina_1' ORDER BY time desc LIMIT 1"
			query3 = "SELECT * as temperatura FROM climatizacion WHERE mote_id = 'linti_control' ORDER BY time desc LIMIT 1"
			query4 = "SELECT * as temperatura FROM climatizacion WHERE mote_id = 'linti_servidores' ORDER BY time desc LIMIT 1"
			print query
			print query2
			print query3
			print query4
			res = self.client.query(query) #Consulta meramente de prueba
			res2 = self.client.query(query2) #Consulta meramente de prueba
			res3 = self.client.query(query3) #Consulta meramente de prueba
			res4 = self.client.query(query4) #Consulta meramente de prueba
		except:
			print("Error al efectuar la consulta")
		try:
			self.temp_amb =  res3[('climatizacion', None)].next()['temperature']
		except:
			pass
		else:
			print "sdfsdfdsfsfddsfsdfsdfdsfdsfdsfdsf"
			print res
			#~ self.ids["scroll_grid"].clear_widgets()
			#cocina
			for re in res:
				#~ print "............."
				#~ datosactuales_control = self.procesar_datos_cocina(re[-1])
				#~ datosactuales_coc = self.procesar_datos_cocina(re[-2])


				#~ for dato in range(len(self.etiquetas_coc)):
					#~ self.ids[self.etiquetas_coc[dato]].text = datosactuales_coc[dato]
					#~ self.ids[self.etiquetas_control[dato]].text = datosactuales_control[dato]

				print "......--------------------------------"

				print re
				print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

				temp_color = self.calcular_color(re[-1]["temperature"])
				self.ids["temperature_coc"].text = temp_color
				self.ids["temperature_coc"].texture_update()

			#oficina
			for re in res2:
				temp_color = self.calcular_color(re[-1]["temperature"])
				self.ids["temperature"].text = temp_color
				self.ids["temperature"].texture_update()
			print "*************************control*********"
			
			#control
			#for re in res3:
				#temp_color = self.calcular_color(re[-1]["temperature"])
				#self.ids["temperature_cont"].text = temp_color
				#self.ids["temperature_cont"].texture_update()

			for re in res4:
				temp_color = self.calcular_color(re[-1]["temperature"])
				self.ids["temperature_serv"].text = temp_color
				self.ids["temperature_serv"].texture_update()


				#~ self.ids["scroll_grid"].add_widget(line)

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
