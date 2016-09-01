#!/usr/bin/env python
# -*- coding: utf-8 -*-
#kivy
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
#python
from functools import partial
import datetime
class Mota(Button):
	def __init__(self, data, historial, temp_amb):
		super(Mota, self).__init__()
		self.name = data["mote_id"]
		self.motion = data["motion"]
		self.date = data["time"]
		self.text = str(data["temperature"])
		self.temperature = data["temperature"]
		self.pos = 400,400
		#~ self.setTemperature(data["temperature"], temp_amb)
		self.actualizar(temp_amb, historial)

	def getName(self):
		return self.name

	def setTemperature(self, temp, temp_amb):
		self.temperature = temp
		self.text = temp
		self.calcular_color(temp_amb)

	def getTemperatura(self):
		return self.temperature

	def actualizar(self, temp, historial):
		temp_color = self.calcular_color(temp)
		self.text = temp_color
		self.texture_update()
		self.bind(on_release=partial(self.historial_mota,historial))

	def historial_mota(self, historial, *args):
		print args
		layout = GridLayout(cols=4, spacing=30, size_hint_y=None)
		layout.bind(minimum_height=layout.setter('height'))
		print "....................***************************................................"
		print historial
		for re in historial:
			print re
			for r in re:
				print r
				temp_color = self.calcular_color(r['temperature'])
				layout.add_widget(Label(text=temp_color, markup= True))
				layout.add_widget(Label(text=str(r["current"])))
				layout.add_widget(Label(text=str(r["time"])))
				layout.add_widget(Label(text=str(r["motion"])))


			#~ layout.add_widget(Button(text="Cerrar"))

			contenido = ScrollView(size_hint=(1, 1), size=(400,400))
			contenido.add_widget(layout)
			popup = Popup(title='Historial '+self.name, content=contenido, size_hint=(.8, .6))
			popup.open()

	def calcular_color(self, temp_amb):
		print ('´´´´´´´´´´´´´´´´´')
		print (self.text, temp_amb)
		if self.temperature > temp_amb + 5:
			return "[color=f10000]" + self.text+"[/color]"
		else:
			return "[color=13E400]"+self.text+"[/color]"
		#return "[color=f10000]" + str(self.text)+"[/color]" if float(self.text) > float(temp_amb) + 5 else "[color=13E400]"+str(self.text)+"[/color]"


class Piso(Screen):
	def __init__(self, num, motas_ids, img, client, spinner, *args):
		super(Piso, self).__init__(*args)
		self.name = "piso_"+str(num)
		self.num = num
		self.client = client
		self.info_motas = {}
		self.procesar_datos(motas_ids)

		with self.canvas.before:
			Rectangle(size=Window.size, pos=(0,0), source=img)

		self.flayout = self.ids["flayout_id"]
		self.sp = spinner
		self.add_widget(self.sp)
		self.sp.size_hint= (.09,.05)
		spinner.bind(text=self.cambiar_piso)
		#~ self.flayout.texture_update()

	def cambiar_piso(self, *args):
		print "cambio de piso"
		print args

	def agregar_motas(self):
		for each in self.info_motas.items():
			print each
			#~ self.ids["Piso_"+str(self.num)].add_widget(each)
			self.flayout.add_widget(each[1])

	def procesar_datos(self, motas_ids):
		query = "SELECT * as temperatura FROM climatizacion WHERE mote_id = '"+motas_ids[0]+"' ORDER BY time desc LIMIT 1"
		res = self.client.query(query).items()[0][1].next()

		historial = self.client.query("SELECT mote_id, temperature, motion, current, time FROM climatizacion WHERE mote_id = '"+motas_ids[0]+"' ORDER BY time desc LIMIT 50")

		self.info_motas[res["mote_id"]] = Mota(res, historial, res['temperature'])

		motas_ids.pop(0)
		for s in motas_ids:
			query = "SELECT * as temperatura FROM climatizacion WHERE mote_id = '"+s+"' ORDER BY time desc LIMIT 1"
			res = self.client.query(query).items()[0][1].next()

			historial = self.client.query("SELECT mote_id, temperature, motion, current, time FROM climatizacion WHERE mote_id = '"+s+"' ORDER BY time desc LIMIT 50")

			self.info_motas[res["mote_id"]] = Mota(res, historial, self.info_motas["linti_control"].getTemperatura())

		self.ids['fecha'].text = 'Ultima actualización: '+datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y %H:%M')

	def actualizar_mapa(self):
		try:
			#~ query = []
			query = {}

			for s in self.info_motas.keys():
				query[s] = "SELECT mote_id, temperature, motion, current, time FROM climatizacion WHERE mote_id = '"+s+"' ORDER BY time desc LIMIT 50"
			res = {}
			for q in query.items():
				print "------------------------------------________________--------------------------------------------"
				print q[0]
				print q[1]
				#~ res.append(self.client.query(q)) #Consulta meramente de prueba
				res[q[0]] = self.client.query(q[1]) #Consulta meramente de prueba
			try:
				self.temp_amb = res['linti_control']['temperature']#[0][('climatizacion', None)].next()['temperature']
			except:
				print "asdkmaskdnkasndasmd---------------------------------------------------------------"
				#~ print res['linti_control'][0].next()
		except Exception, e:
			print("Error al efectuar la consulta 1 "+str(e))
		else:
			#~ self.temp_amb = res['linti_control']['temperature']#[('climatizacion', None)].next()['temperature']
			for s in self.info_motas.items():
				print res[s[0]]
				print res[s[0]]['temperature']
				print "}{}{}{}{}{}{}}}}}}}}{{{{{{{{{{{{{{{{{{{{}}}}}}}}}}}}}"
				temp_color = s[1].calcular_color(res[s[0]].items()[0][1].next()['temperature'])
				s[1].text = temp_color
				s[1].texture_update()
				s[1].bind(on_release=partial(s[1].historial_mota,res[s[0]]))
			self.ids['fecha'].text = 'Ultima actualización: '+datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y %H:%M')
