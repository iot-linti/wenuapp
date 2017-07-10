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
import time
#import shelve
import json
#kivymd

from kivymd.snackbar import Snackbar
from kivy.metrics import dp
from kivy.uix.image import Image
from kivymd.button import MDRaisedButton
from kivymd.label import MDLabel
from kivymd.list import ILeftBody, ILeftBodyTouch, IRightBodyTouch
from kivymd.navigationdrawer import MDNavigationDrawer as NavigationDrawer
from kivymd.selectioncontrols import MDCheckbox
from kivymd.theming import ThemeManager
from kivymd.dialog import MDDialog
from kivymd.time_picker import MDTimePicker
from kivymd.date_picker import MDDatePicker
from kivymd.bottomsheet import MDListBottomSheet, MDGridBottomSheet
#~ from kivymd.spinner import MDSpinner

class Mota(Button):
	def __init__(self, data, historial, temp_amb, client):
		super(Mota, self).__init__()
		#try temporal hasta que esten terminados de cargar los datos en las tablas nuevas
		self.name = data._id
		self.piso = data.level_id
                # self.date = data.time # FIXME: porque esta esta
		self.client = client
		self.historial = []
		print "historial"
		print historial
		#~ print list(historial)
		self.text = str(historial[0])
		self.temperature = historial[0]
		self.temp_amb = temp_amb
		#~ try:
		res = data.resolution.split(",")
		res = int(res[0][1:]),int(res[1][:-1])
		self.orig_size = res#eval(data["resolucion"])#Window.size#(1280, 960)
		#~ orig_size = Window.size#(1280, 960)
		#~ img.size = translate(orig_size, Window.size, *img.size)
		self.pos = self.translate(self.orig_size, Window.size, data.x, data.y)
		self.actualizar(temp_amb, historial[0])

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

	def historial_mota(self, temp_amb, *args):
		bs = MDGridBottomSheet()
		layout_pop = GridLayout(cols=1, rows=2)
		layout = GridLayout(cols=4, spacing=30, size_hint_y=None)
		layout.bind(minimum_height=layout.setter('height'))
		
		#~ if len(self.historial) == 0:
		self.historial = self.client.Measurement.where(mota_id=self.name)
		
		bs = MDListBottomSheet()
		for re in self.historial:
			for r in re:
				mov = "Si" if r["movimiento"] == True else "No"
				text = '{:^10}'.format(str(r['temperatura']))+'{:^50}'.format(str(r["corriente"]))+'{:^50}'.format(str(r["time"]))+'{:^20}'.format(mov)
				if (self.temp_amb + 5 < r['temperatura']):
					bs.add_item(text, lambda x: x, icon='weather-hail')#self.callbaack(x))
				elif (self.temp_amb - 5 < r['temperatura']):
					bs.add_item(text, lambda x: x, icon='weather-sunny')#, icon='alert-circle-outline')
				else:
					bs.add_item(text, lambda x: x)
		bs.add_item("Algo mas", lambda x: x)
		bs.add_item("Apagar", self.apagar_mota, icon='clipboard-account')
		bs.open()

	def apagar_mota(self, evt):
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
		self.client.write_points(json_body)

	def calcular_color(self, temp, temp_amb):
		if temp > 1000:
			return "[color=FFD800]Low battery[/color]"
		elif temp > temp_amb + 5:
			return "[color=f10000]" + str(temp)+"[/color]"
		else:
			return "[color=13E400]"+str(temp)+"[/color]"

class Piso(Screen):
	def __init__(self, num, sensores, img, client, *args):
		super(Piso, self).__init__(*args)
		self.name = "piso_"+str(num)
		self.id = self.name
		self.num = num
		self.client = client
		self.info_motas = {}
		self.sensores = sensores
		#~ self.procesar_datos(sensores)

		with self.canvas.before:
			Rectangle(size=Window.size, pos=(0,0), source=img, allow_stretch=False)

		self.flayout = self.ids["flayout_id"]
		
	def on_pre_enter(self):
		if self.sensores != None:
			Snackbar(text="Espere un momento mientras se cargan las motas.").show()
			
	def on_enter(self):
		if self.sensores != None:
			print "Carga sensores"
			#~ self.sp = MDSpinner()
			#~ self.flayout.add_widget(self.sp)
			self.procesar_datos()
			self.agregar_motas()
			self.sensores = None
			Snackbar(text="Carga completada.").show()

	def getName(self):
		return self.name

	def agregar_motas(self):
		for each in self.info_motas.items():
			self.flayout.add_widget(each[1])

	def procesar_datos(self):
		control = self.client.Mote.first_where(mote_id='linti_control')
		if control is None:
			# FIXME: Deberíamos tener algo más genérico
			raise Exception('No existe linti_control, pensar otra forma de implementar esto')

                historial = list(self.client.Measurement.where(mote_id='linti_control')) #NO DEVUELVE NADA

		temperature = historial[0].temperature if historial else float('nan')
		historial = [15]  #QUITAR HARDCODEO
		self.info_motas[control.mote_id] = Mota(control, historial, temperature, self.client)
		for sen in self.sensores:
			#~ print "\nProcesando un sensor\n"
			#~ historial = self.client.Measurement.where(mota_id=sen.mote_id) #NO DEVUELVE NADA
			#~ historial = self.client.Measurement.first_where(mota_id=sen.mote_id) #FIX ME
			print historial
			historial = [25] #QUITAR HARDCODEO
			#~ print "\nSe cargo el historial\n"
			self.info_motas[sen.mote_id] = Mota(sen, historial, self.info_motas["linti_control"].getTemperatura(), self.client)
			#~ print "\nSe agrego la mota\n"

		self.ids['fecha'].text = 'Ultima actualización: '+datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y %H:%M')

	def actualizar_mapa(self):
		try:
			#~ query = []
			query = {}

			for s in self.info_motas.keys():
				query[s] = "SELECT mota_id, temperatura, movimiento, corriente, time FROM medicion WHERE mota_id = '"+s+"' ORDER BY time desc LIMIT 50"
			res = {}
			for q in query.items():
				#~ res.append(self.client.query(q)) #Consulta meramente de prueba
				res[q[0]] = self.client.query(q[1])
			try:
				self.temp_amb = res['linti_control']['temperatura']#[0][('climatizacion', None)].next()['temperature']
			except:
				print "Error x"
		except Exception, e:
			print("Error al efectuar la consulta 1 "+str(e))
		else:
			#~ self.temp_amb = res['linti_control']['temperature']#[('climatizacion', None)].next()['temperature']
			for s in self.info_motas.items():
				temp_color = s[1].calcular_color(res[s[0]].items()[0][1].next()['temperatura'], self.temp_amb)
				s[1].text = temp_color
				s[1].texture_update()
				s[1].bind(on_release=partial(s[1].historial_mota,res[s[0]]))
			self.ids['fecha'].text = 'Ultima actualización: '+datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y %H:%M')



	def config_mota_pos(self):
		mfp = MakeFilePos(self.info_motas, self.client)
		self.add_widget(mfp)
		mfp.size = self.parent.size
		self.actualizar_mapa


class MakeFilePos(Widget):

	def __init__(self, motas, cli, *args):
		super(MakeFilePos, self).__init__()
		self.motas = motas
		self.motas2 = motas.copy()
		self.client = cli
		self.m_pos = {}
		self.size = Window.size
		self.pos = 0,0
		key = self.motas2.keys()[0]
		l = MDLabel(text="Ingrese posición de la mota: "+str(key), pos_hint={'top':1.44,'right':.06})
		self.add_widget(l)
		#del self.motas2[key]
		#~ self.size = self.parent.size

	def calc_pos(self, tx, ty, key):
		pos = (tx-(self.motas[str(key)].size[0]/2),ty-(self.motas[str(key)].size[1]/2))
		return map(int, pos)

	def on_touch_down(self, touch):
		if len(self.children) > 0:
			self.remove_widget(self.children[-1])
		if len(self.motas2) > 0:
			key = self.motas2.keys()[0]
			self.m_pos[str(key)] = self.calc_pos(touch.pos[0], touch.pos[1], key)
			del self.motas2[key]
			if len(self.motas2) > 0:
				key = self.motas2.keys()[0]
				l = MDLabel(text="Ingrese posición de la mota: "+str(key), pos_hint={'top':1.44,'right':.06})
				self.add_widget(l)
			else:
				l = MDLabel(text="Haga click para finalizar", pos_hint={'top':1.44,'right':.06})
				self.add_widget(l)
		else:
			for m in self.motas.keys():
				mote = self.client.Mote.first_where(mote_id=m, level_id = self.motas[m].get_piso())
				mote.x = self.m_pos[m][0];
				mote.y = self.m_pos[m][1];
				mote.resolution = str(Window.size)
				mote.save()
				self.motas[str(m)].pos = self.motas[str(m)].pos = self.motas[str(m)].translate(self.motas[str(m)].orig_size, Window.size, self.m_pos[m][0],self.m_pos[m][1])
			self.parent.remove_widget(self)
		return True
