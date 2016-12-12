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
from kivy.uix.floatlayout import FloatLayout
#python
from functools import partial
import datetime
#import shelve
import json
#kivymd

import kivymd.snackbar as Snackbar
from kivy.metrics import dp
from kivy.uix.image import Image
from kivymd.bottomsheet import MDListBottomSheet, MDGridBottomSheet
from kivymd.button import MDIconButton
from kivymd.button import MDRaisedButton
from kivymd.label import MDLabel
from kivymd.list import ILeftBody, ILeftBodyTouch, IRightBodyTouch
from kivymd.navigationdrawer import NavigationDrawer
from kivymd.selectioncontrols import MDCheckbox
from kivymd.theming import ThemeManager
from kivymd.dialog import MDDialog
from kivymd.time_picker import MDTimePicker
from kivymd.date_picker import MDDatePicker

class Mota(Button):
	def __init__(self, data, historial, temp_amb, client):
		super(Mota, self).__init__()
		#try temporal hasta que esten terminados de cargar los datos en las tablas nuevas
		print data
		print "daaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
		self.name = data["mota_id"]
		self.piso = data["piso_id"]
		self.date = data["time"]
		self.client = client
		hist = historial.items()[0][1].next()["temperatura"]
		self.text = str(hist)
		self.temperature = hist
		self.temp_amb = temp_amb
		#~ try:
		res = data["resolucion"].split(",")
		res = int(res[0][1:]),int(res[1][:-1])
		orig_size = res#eval(data["resolucion"])#Window.size#(1280, 960)
		#~ orig_size = Window.size#(1280, 960)
		#~ img.size = translate(orig_size, Window.size, *img.size)
		self.pos = self.translate(orig_size, Window.size, data["x"], data["y"])
		self.actualizar(temp_amb, historial)

	def get_piso(self):
		return self.piso


	def translate(self, orig_size, new_size, x, y):
		ow, oh = orig_size
		nw, nh = new_size
		return (x * nw / ow, y * nh / oh)

	def getName(self):
		return self.name

	def setTemperature(self, temp, temp_amb):
		self.temperature = temp
		self.text = temp
		#~ self.calcular_color(temp_amb)

	def getTemperatura(self):
		return self.temperature

	def actualizar(self, temp, historial):
		temp_color = self.calcular_color(self.temperature, temp)
		self.text = temp_color
		self.texture_update()
		self.bind(on_release=partial(self.historial_mota,historial, temp))

	def historial_mota(self, historial, temp_amb, *args):
		#print args
		bs = MDGridBottomSheet()
		layout_pop = GridLayout(cols=1, rows=2)
		layout = GridLayout(cols=4, spacing=30, size_hint_y=None)
		layout.bind(minimum_height=layout.setter('height'))


		bs = MDListBottomSheet()
		#~ print self.callbaack()
		#~ self.ids["bottomsheet"].add_widget(NavigationDrawerIconButton(text="sdads"))
		for re in historial:
			#print re
			for r in re:
				#temp_color = self.calcular_color(r['temperatura'], temp_amb)
				text = '{:^10}'.format(str(r['temperatura']))+'{:^50}'.format(str(r["corriente"]))+'{:^50}'.format(str(r["time"]))+'{:^20}'.format(str(r["movimiento"]))
				if (self.temp_amb + 5 < r['temperatura']):
					bs.add_item(text, lambda x: x, icon='weather-hail')#self.callbaack(x))
				elif (self.temp_amb - 5 < r['temperatura']):
					bs.add_item(text, lambda x: x, icon='weather-sunny')#, icon='alert-circle-outline')
				else:
					bs.add_item(text, lambda x: x)
		bs.add_item("Algo mas", lambda x: x)
		bs.add_item("Apagar", self.apagar_mota, icon='clipboard-account')
		#bs.add_item("Here's another!", lambda x: x, icon='nfc')
		bs.open()

	def apagar_mota(self, evt):
		print "apaga "+str(self.name)
		json_body = [
			{
				"measurement": "accion",
				"tags": {
					"mota_id": self.name,
					"piso_id": self.piso
				},
				#~ "time": '2016-10-04T20:26:34Z',
				"fields": {
					"apagar": "true"
				}
			}
		]

		#~ print json_body
		self.client.write_points(json_body)

	def calcular_color(self, temp, temp_amb):
		print temp > 1000
		print temp
		if temp > 1000:
			return "[color=FFD800]Low battery[/color]"
		elif temp > temp_amb + 5:
			return "[color=f10000]" + str(temp)+"[/color]"
		else:
			return "[color=13E400]"+str(temp)+"[/color]"
		#return "[color=f10000]" + str(self.text)+"[/color]" if float(self.text) > float(temp_amb) + 5 else "[color=13E400]"+str(self.text)+"[/color]"


class Piso(Screen):
	def __init__(self, num, sensores, img, client, *args):
		super(Piso, self).__init__(*args)
		self.name = "piso_"+str(num)
		self.num = num
		self.client = client
		self.info_motas = {}
		print "+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-++-+-+-++-++-++-+"
		print sensores
		self.procesar_datos(sensores)

		with self.canvas.before:
			Rectangle(size=Window.size, pos=(0,0), source=img, allow_stretch=False)
		print self.ids
		self.flayout = FloatLayout()

		#self.flayout = self.ids["flayout_id"]

	def getName(self):
		return self.name

	def agregar_motas(self):
		for each in self.info_motas.items():
			print each
			#~ self.ids["Piso_"+str(self.num)].add_widget(each)
			self.flayout.add_widget(each[1])

	def procesar_datos(self, sensores):
		query = "SELECT * as temperatura FROM mota WHERE mota_id = 'linti_control' ORDER BY time desc LIMIT 1"
		print query
		print sensores
		res = self.client.query(query).items()[0][1].next()
		print res
		print "reeeeeeeeeeeeeeeeeeessssssssssssss"

		#~ historial = self.client.query("SELECT mota_id, temperatura, motion, current, time FROM medicion WHERE mota_id = 'linti_control' ORDER BY time desc LIMIT 50")
		historial = self.client.query("SELECT mota_id, temperatura, movimiento, corriente, time FROM medicion WHERE mota_id = 'linti_control' ORDER BY time desc LIMIT 50")

		self.info_motas[res["mota_id"]] = Mota(res, historial, historial.items()[0][1].next()['temperatura'], self.client)

		#ctrl = motas_ids.pop(0)
		#~ print "???????????????SENSORES?????????????????????"
		#~ print sensores
		for sen in sensores:
			print sen
			for s in sen:
				query = "SELECT * as temperatura FROM mota WHERE mota_id = '"+s["mota_id"]+"' ORDER BY time desc LIMIT 1"
				#~ print query
				res = self.client.query(query).items()[0][1].next()

				historial = self.client.query("SELECT mota_id, temperatura, movimiento, corriente, time FROM medicion WHERE mota_id = '"+s["mota_id"]+"' ORDER BY time desc LIMIT 50")

				self.info_motas[res["mota_id"]] = Mota(res, historial, self.info_motas["linti_control"].getTemperatura(), self.client)

		print "IDsss"
		print self.ids
		#self.ids['fecha'].text = 'Ultima actualización: '+datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y %H:%M')
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
				temp_color = s[1].calcular_color(res[s[0]].items()[0][1].next()['temperatura'], self.temp_amb)
				s[1].text = temp_color
				s[1].texture_update()
				s[1].bind(on_release=partial(s[1].historial_mota,res[s[0]]))
			self.ids['fecha'].text = 'Ultima actualización: '+datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y %H:%M')



	def config_mota_pos(self):
		mfp = MakeFilePos(self.info_motas, self.ids["config_mota_pos"], self.client)
		self.add_widget(mfp)
		mfp.size = self.parent.size
		self.actualizar_mapa


class MakeFilePos(Widget):

	def __init__(self, motas, btn_pos, cli, *args):
		super(MakeFilePos, self).__init__()
		self.motas = motas
		self.motas2 = motas.copy()
		self.btn_pos = btn_pos
		self.client = cli
		self.m_pos = {}
		#~ self.size = self.parent.size

	def calc_pos(self, tx, ty, key):
		return tx-(self.motas[str(key)].size[0]/2),ty-(self.motas[str(key)].size[1]/2)

	def on_touch_down(self, touch):
		print touch
		print touch.spos
		if (not self.btn_pos.collide_point(touch.x,touch.y)):

			if len(self.motas2) > 0:
				key = self.motas2.keys()[0]
				l = Label(text="[color=00ff60]Ingrese posición de la mota: "+str(key)+"[/color]", pos=(400,200), markup=True)
				self.add_widget(l)
				self.m_pos[str(key)] = self.calc_pos(touch.pos[0], touch.pos[1], key)
				#touch.pos[0]-(self.motas[str(key)].size[0]/2),touch.pos[1]-(self.motas[str(key)].size[1]/2)
				del self.motas2[key]
			else:
				for m in self.motas.keys():
					print self.motas[m].get_piso()
					json_body = [
							{
								"measurement": "mota",
								"tags": {
									"mota_id": m,
									"piso_id": self.motas[m].get_piso()
								},
								"time": 0,
								"fields": {
									"x": self.m_pos[m][0],
									"y": self.m_pos[m][1],
									"resolucion": str(Window.size)
								}
							}
						]

					#~ print json_body
					self.client.write_points(json_body)
					#~ m.pos_hint = {'top':arch[m.name][0], 'right':arch[m.name][1]}
					self.motas[str(m)].pos = self.calc_pos(self.m_pos[m][0],self.m_pos[m][1], m)
					#(self.m_pos[m][0]-(self.motas[str(m)].size[0]/2),self.m_pos[m][1]-(self.motas[str(m)].size[1]/2))
				#~ self.parent.actualizar_mapa()
				self.parent.remove_widget(self)
		return True
