#!/usr/bin/env python
# -*- coding: utf-8 -*-
#kivy
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
#python
from functools import partial
import datetime
#import shelve
import json

class Mota(Button):
	def __init__(self, data, historial, temp_amb, posiciones):
		super(Mota, self).__init__()
		#try temporal hasta que esten terminados de cargar los datos en las tablas nuevas
		print data
		print "daaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
		try:
			self.name = data["mota_id"]
		except:
			self.name = data["mota_id"]
		try:
			self.motion = data["movimiento"] #antiguamente llamado motion
		except:
			self.motion = data["motion"]
		self.date = data["time"]
		try:
			self.text = str(data["temperatura"])
		except:
			self.text = str(data["temperatura"])
		try:
			self.temperature = data["temperatura"]
		except:
			self.temperature = data["temperatura"]
		print "pooooooooooooooooooooooooooossssssssssssss"
		print self.name
		print posiciones
		#print posiciones[str(self.name)]
		print "pooooooooooooooooooooooooooossssssssssssss"
		try:
			self.pos = posiciones[str(self.name)]
		except:
			self.pos = (400,400)
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
				#hasta que se solucione lo de las tablas
				try:
					temp_color = self.calcular_color(r['temperatura'])
					layout.add_widget(Label(text=temp_color, markup= True))
					layout.add_widget(Label(text=str(r["current"])))
					layout.add_widget(Label(text=str(r["time"])))
					layout.add_widget(Label(text=str(r["motion"])))
				except:
					temp_color = self.calcular_color(r['temperatura'])
					layout.add_widget(Label(text=temp_color, markup= True))
					layout.add_widget(Label(text=str(r["corriente"])))
					layout.add_widget(Label(text=str(r["time"])))
					layout.add_widget(Label(text=str(r["movimiento"])))


			#~ layout.add_widget(Button(text="Cerrar"))

			contenido = ScrollView(size_hint=(1, 1), size=(400,400))
			contenido.add_widget(layout)
			popup = Popup(title='Historial '+self.name, content=contenido, size_hint=(.8, .6))
			popup.open()

	def calcular_color(self, temp_amb):
		if self.temperature > temp_amb + 5:
			return "[color=f10000]" + self.text+"[/color]"
		else:
			return "[color=13E400]"+self.text+"[/color]"
		#return "[color=f10000]" + str(self.text)+"[/color]" if float(self.text) > float(temp_amb) + 5 else "[color=13E400]"+str(self.text)+"[/color]"


class Piso(Screen):
	def __init__(self, num, sensores, img, client, pisos, *args):
		super(Piso, self).__init__(*args)
		self.name = "piso_"+str(num)
		self.num = num
		self.client = client
		self.info_motas = {}
		print "+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-++-+-+-++-++-++-+"
		print sensores
		self.procesar_datos(sensores)

		with self.canvas.before:
			Rectangle(size=Window.size, pos=(0,0), source=img)

		self.flayout = self.ids["flayout_id"]
		#~ self.sp = spinner
		sp_vals = []
		for v in pisos:
			sp_vals.append(str(v[0]["piso_id"]))
		#~ self.sp = Spinner(text=str(num), values=sp_vals, size_hint= (.09,.05), pos_hint={'top':1,'left':.9})
		#~ self.add_widget(self.sp)
		#~ self.sp.size_hint= (.09,.05)
		#~ self.sp.bind(text=self.cambiar_piso)
		#~ self.flayout.texture_update()

		layout = GridLayout(cols=1, size_hint_y=None)
		layout.bind(minimum_height=layout.setter('height'))
		for r in sp_vals:
			print r
			btn = Button(text=r)
			btn.bind(on_release=self.cambiar_piso)
			layout.add_widget(btn)
		contenido = ScrollView(size_hint=(1, 1))
		contenido.add_widget(layout)
		self.pisos = Popup(title='Pisos', content=contenido, pos_hint={'top':1,'left':.1},size_hint=(.4, .9))
		#~ self.add_widget(self.pisos)
		#~ self.pisos.open()
		self.btn_popup_pisos = Button(text="Pisos", pos_hint={'top':1,'left':.1}, size_hint=(.1, .1))
		self.btn_popup_pisos.bind(on_press=self.abrir_popup_pisos)
		self.add_widget(self.btn_popup_pisos)

	def abrir_popup_pisos(self, *args):
		self.pisos.open()

	def cambiar_piso(self, *args):
		print "cambio de piso"
		print args
		self.parent.current = "piso_"+args[0].text
		self.pisos.dismiss()
		#~ self.sp.text = str(self.num)

	def agregar_motas(self):
		for each in self.info_motas.items():
			print each
			#~ self.ids["Piso_"+str(self.num)].add_widget(each)
			self.flayout.add_widget(each[1])

	def procesar_datos(self, sensores):
		query = "SELECT * as temperatura FROM medicion WHERE mota_id = 'linti_control' ORDER BY time desc LIMIT 1"
		print query
		print sensores
		res = self.client.query(query).items()[0][1].next()
		print res
		print "reeeeeeeeeeeeeeeeeeessssssssssssss"

		historial = self.client.query("SELECT mota_id, temperatura, motion, current, time FROM medicion WHERE mota_id = 'linti_control' ORDER BY time desc LIMIT 50")

		try:
			posiciones_arch = open("motas.json")
		except IOError:
			posiciones_arch = open("motas.json","w")
			d={}
			json.dump(d,posiciones_arch)
			posiciones_arch.close()
			posiciones_arch = open("motas.json")
		finally:
			posiciones = json.load(posiciones_arch)

		self.info_motas[res["mota_id"]] = Mota(res, historial, res['temperatura'], posiciones)

		#ctrl = motas_ids.pop(0)
		print "????????????????????????????????????"
		print sensores
		for s in sensores:
			print s[0]
			query = "SELECT * as temperatura FROM medicion WHERE mota_id = '"+s[0]["mota_id"]+"' ORDER BY time desc LIMIT 1"
			print query
			res = self.client.query(query).items()[0][1].next()

			historial = self.client.query("SELECT mota_id, temperatura, movimiento, corriente, time FROM medicion WHERE mota_id = '"+s[0]["mota_id"]+"' ORDER BY time desc LIMIT 50")

			self.info_motas[res["mota_id"]] = Mota(res, historial, self.info_motas["linti_control"].getTemperatura(), posiciones)

		self.ids['fecha'].text = 'Ultima actualización: '+datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y %H:%M')
		#motas_ids.insert(0, ctrl)

	def actualizar_mapa(self):
		try:
			#~ query = []
			query = {}

			for s in self.info_motas.keys():
				query[s] = "SELECT mota_id, temperatura, movimiento, corriente, time FROM medicion WHERE mota_id = '"+s+"' ORDER BY time desc LIMIT 50"
			res = {}
			for q in query.items():
				print "------------------------------------________________--------------------------------------------"
				print q[0]
				print q[1]
				#~ res.append(self.client.query(q)) #Consulta meramente de prueba
				res[q[0]] = self.client.query(q[1])
			try:
				self.temp_amb = res['linti_control']['temperatura']#[0][('climatizacion', None)].next()['temperature']
			except:
				print "asdkmaskdnkasndasmd---------------------------------------------------------------"
				#~ print res['linti_control'][0].next()
		except Exception, e:
			print("Error al efectuar la consulta 1 "+str(e))
		else:
			#~ self.temp_amb = res['linti_control']['temperature']#[('climatizacion', None)].next()['temperature']
			for s in self.info_motas.items():
				print res[s[0]]
				print res[s[0]]['temperatura']
				print "}{}{}{}{}{}{}}}}}}}}{{{{{{{{{{{{{{{{{{{{}}}}}}}}}}}}}"
				temp_color = s[1].calcular_color(res[s[0]].items()[0][1].next()['temperatura'])
				s[1].text = temp_color
				s[1].texture_update()
				s[1].bind(on_release=partial(s[1].historial_mota,res[s[0]]))
			self.ids['fecha'].text = 'Ultima actualización: '+datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y %H:%M')



	def config_mota_pos(self):
		#~ arch = shelve.open("motas.txt")
		#~ for mota in self.info_motas:
			#~ print mota
			#~ l = Label(text="Ingrese posición de la mota: "+str(mota), pos=(400,200))
			#~ self.add_widget(l)
		mfp = MakeFilePos(self.info_motas)
		self.add_widget(mfp)
		mfp.size = self.parent.size


class MakeFilePos(Widget):

	def __init__(self, motas, *args):
		super(MakeFilePos, self).__init__()
		self.motas = motas
		self.motas2 = motas.copy()
		#~ self.size = self.parent.size

	def on_touch_down(self, touch):
		print touch
		print touch.spos
		jarch = open("motas.json")
		arch = json.load(jarch)
		jarch = open("motas.json","w")
		if len(self.motas2) > 0:
			key = self.motas2.keys()[0]
			l = Label(text="Ingrese posición de la mota: "+str(key), pos=(400,200), color=(0,1,1))
			self.add_widget(l)
			arch[str(key)] = touch.pos#.spos
			del self.motas2[key]
		else:
			for m in self.motas.keys():
				#~ m.pos_hint = {'top':arch[m.name][0], 'right':arch[m.name][1]}
				self.motas[str(m)].pos = (arch[str(m)][0]-(self.motas[str(m)].size[0]/2),arch[str(m)][1]-(self.motas[str(m)].size[1]/2))
			self.parent.remove_widget(self)
		json.dump(arch,jarch)
		jarch.close()
		return True
