#!/usr/bin/env python
# -*- coding: utf-8 -*-
#kivy
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle
from kivy.core.window import Window
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
		
	def historial_mota(self, historial):
		layout = GridLayout(cols=4, spacing=30, size_hint_y=None)
		layout.bind(minimum_height=layout.setter('height'))
		for re in res:
			for r in re:
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
		#~ a =  "[color=f10000]"
		#~ b = str(self.text)
		#~ c = "[/color]"
		#~ print a+b+c
		#~ d = float(temp_amb) 
		#~ f = "[color=13E400]"
		#~ print f+b+c
		#~ return '10'
		print ('´´´´´´´´´´´´´´´´´')
		print (self.text, temp_amb)
		if self.temperature > temp_amb + 5:
			return "[color=f10000]" + self.text+"[/color]"
		else: 
			return "[color=13E400]"+self.text+"[/color]"
		#return "[color=f10000]" + str(self.text)+"[/color]" if float(self.text) > float(temp_amb) + 5 else "[color=13E400]"+str(self.text)+"[/color]"
		

class Piso(Screen):
	def __init__(self, num, motas_ids, img, client, *args):
		super(Piso, self).__init__(*args)
		self.name = "piso_"+str(num)
		self.num = num
		self.client = client
		self.info_motas = {}
		self.procesar_datos(motas_ids)
		
		with self.canvas.before:
			Rectangle(size=Window.size, pos=(0,0), source=img)
			
		self.flayout = self.ids["flayout_id"]
		#~ self.flayout.texture_update()
		
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
				self.ids[s].bind(on_release=partial(self.historial_mota,s))
			self.ids['fecha'].text = 'Ultima actualización: '+datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y %H:%M')
