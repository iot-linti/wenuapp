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
from kivy.uix.boxlayout import BoxLayout
#~ from kivy.uix.popup import Popup
#~ from kivy.uix.spinner import Spinner
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
#~ from kivy.uix.image import AsyncImage
from kivy.metrics import dp
#~ from kivy.uix.image import Image
#~ from kivy.uix.video import Video
#~ from kivy.uix.scatter import Scatter
#python
from functools import partial
import datetime
import time
#import shelve
import json
#kivymd

from kivymd.snackbar import Snackbar
from kivymd.button import MDRaisedButton
from kivymd.label import MDLabel
from kivymd.list import ILeftBody, ILeftBodyTouch, IRightBodyTouch
from kivymd.navigationdrawer import MDNavigationDrawer as NavigationDrawer
from kivymd.selectioncontrols import MDCheckbox
from kivymd.theming import ThemeManager
from kivymd.dialog import MDDialog
#~ from kivymd.time_picker import MDTimePicker
#~ from kivymd.date_picker import MDDatePicker
from kivymd.bottomsheet import MDListBottomSheet, MDGridBottomSheet
#~ from kivymd.spinner import MDSpinner
#otros
import mjpegviewer

class MotaImage(Widget):
	def __init__(self, src, *args, **kwargs):
		super(MotaImage, self).__init__(**kwargs)
		self.size = 300,300

		self.video = mjpegviewer.MjpegViewer(url=src, size=(300,300))
		self.video.start()
		self.add_widget(self.video)

			
	def on_touch_down(self, touch):
		print "Close"
		if self.collide_point(*touch.pos):
			#~ self.event.cancel()
			self.parent.remove_widget(self)

class Mota(Button):
	"""Clase (Boton) que representa a la mota."""
	def __init__(self, data, historial, temp_amb, client):
		super(Mota, self).__init__()
		#try temporal hasta que esten terminados de cargar los datos en las tablas nuevas
		self.name = data.mote_id
		self.mote_id = data._id
		self.piso = data.level_id
                # self.date = data.time # FIXME: porque esta esta
		self.client = client #Cliente de la bd
		self.historial = [] #Historial de la mota (temperaturas).
		self.text = str(historial[0])
		self.temperature = historial[0]
		self.temp_amb = temp_amb
		#~ try:
		res = data.resolution.split(",")
		res = int(res[0][1:]),int(res[1][:-1])
		self.orig_size = res#eval(data["resolucion"])#Window.size#(1280, 960)
		#~ orig_size = Window.size#(1280, 960)
		#~ img.size = translate(orig_size, Window.size, *img.size)
		#~ t = self.translate(self.orig_size, Window.size, data.x, data.y)
		#~ self.calc_pos(t[0],t[1])
		self.pos = self.translate(self.orig_size, Window.size, data.x, data.y)
		#~ self.pos = data.x, data.y
		self.edit_position = False
		self.actualizar(temp_amb, historial[0])
		#Ip de la camara de la mota
		self.ipv = "http://lihuen:lihuen@163.10.10.103/video4.mjpg"

	def get_piso(self):
		"""Retorna el numero de piso."""
		return self.piso

	def get_picture(self, *evt):
		"""Instancia la clase MotaImage para mostrar el video."""
		self.image = MotaImage(self.ipv)
		#~ self.add_widget(self.image)
		self.parent.add_widget(self.image)
		
	def set_edit(self, val=True):
		"""Cambia si se esta editando la posicion de la mota o no (permite ver el historial al presionar)."""
		self.edit_position = val
		
	def close_picture(self, *evt):
		"""Cierra el video."""
		self.dialog.dismiss()
		#~ Clock.unschedule_interval(self.refresh)
		self.evt_refresh.cancel()

	def translate(self, orig_size, new_size, x, y):
		"""Cambia la posicion de la mota a corde a su posicion original y la resolucion de la pantalla
			del dispositivo en uso."""
		ow, oh = orig_size
		nw, nh = new_size
		#~ print "Translate"
		#~ print x * nw / ow, y * nh / oh
		return (x * nw / ow, y * nh / oh)

	def getName(self):
		"""Retorna el nombre de la mota."""
		return self.name

	def getId(self):
		"""Retorna el id de la mota."""
		return self.mote_id

	def setTemperature(self, temp, temp_amb):
		"""Setea la temperatura de la mota."""
		self.temperature = temp
		self.text = temp
		#~ self.calcular_color(temp_amb)

	def getTemperatura(self):
		"""Retorna la temperatura de la mota."""
		return self.temperature

	def actualizar(self, temp, historial):
		"""Actualiza la temperatura de la mota modificando su color en relación a la temp. ambiente."""
		temp_color = self.calcular_color(self.temperature, temp)
		self.text = temp_color
		self.texture_update()
		self.bind(on_release=partial(self.historial_mota,historial, temp))

	def historial_mota(self, temp_amb, *args):
		"""Muestra el historial de la mota en un MDGridBottomSheet."""
		bs = MDGridBottomSheet()
		layout_pop = GridLayout(cols=1, rows=2)
		layout = GridLayout(cols=4, spacing=30, size_hint_y=None)
		layout.bind(minimum_height=layout.setter('height'))
		
		#~ if len(self.historial) == 0:
		self.historial = self.client.Measurement.where(mota_id=self.name)
		
		bs = MDListBottomSheet()
		for r in self.historial:
			mov = "Si" if r.movement == True else "No"
			#~ print r
			#~ print self.temp_amb
			text = '{:^10}'.format(str(r.temperature))+'{:^50}'.format(str(r.current))+'{:^50}'.format(str(r._updated))+'{:^20}'.format(mov)
			if (self.temp_amb.temperature + 5 < r.temperature):
				bs.add_item(text, lambda x: x, icon='weather-hail')#self.callbaack(x))
			elif (self.temp_amb.temperature - 5 < r.temperature):
				bs.add_item(text, lambda x: x, icon='weather-sunny')#, icon='alert-circle-outline')
			else:
				bs.add_item(text, lambda x: x)
		bs.add_item("Cambiar posicion", self.set_edit, icon='map-marker')
		bs.add_item("Apagar aire", self.apagar_mota, icon='clipboard-account')
		bs.add_item("Ver imagen", self.get_picture, icon='camera')
		bs.open()

	def apagar_mota(self, evt):
		"""Pone en la bd que hay que apagar el aire donde se encuentra la mota."""
		print self.mote_id
		print type(self.mote_id)
		a = self.client.Action(mote_id=self.mote_id, command="turn_off", viewed=False)
		a.create()

	def calcular_color(self, temp, temp_amb):
		"""Calcula el color de la mota segun su temperatura y la del ambiente."""
		if temp > 1000:
			return "[color=FFD800]Low battery[/color]"
		elif temp > temp_amb + 5:
			return "[color=f10000]" + str(temp)+"[/color]"
		else:
			return "[color=13E400]"+str(temp)+"[/color]"
			
	def posicionar(self, pos, *evt):
		"""Actualiza la posicion de la mota en bd."""
		mote = self.client.Mote.first_where(mote_id=self.getName(), level_id = self.get_piso())
		mote.x = int(pos[0]);
		mote.y = int(pos[1]);
		mote.resolution = str(Window.size)
		mote.save()
		self.calc_pos(int(pos[0]),int(pos[1]))
		Snackbar(text="Posicion guardada.").show()
		#~ m = self.client.Mote.first_where(mote_id=self.getName(), level_id = self.get_piso())
		
	def calc_pos(self, tx, ty):
		"""Calcula la nueva posicion."""
		self.x, self.y = (tx-(self.size[0]/2),ty-(self.size[1]/2))
		#~ print self.x, self.y
		#~ print "Calc pos"
		
	def on_touch_down(self, touch):
		if self.edit_position:
			self.posicionar(touch.pos)
			self.edit_position = False
		elif self.collide_point(*touch.pos):
			self.historial_mota(self.historial)

class Piso(Screen):
	"""Clase que representa un piso (Screen) con sus motas, imagen."""
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
		"""Antes de cargar el screen muestra el mensaje si es la primera vez que entra al piso."""
		if self.sensores != None:
			Snackbar(text="Espere un momento mientras se cargan las motas.", duration=2).show()
			
	def on_enter(self):
		"""Cuando carga el piso/screen agrega las motas y muestra mensaje indicando que termino 
			(si es la primera vez que entra al piso)."""
		if self.sensores != None:
			#~ print "Carga sensores"
			#~ self.sp = MDSpinner()
			#~ self.flayout.add_widget(self.sp)
			self.procesar_datos()
			self.agregar_motas()
			self.sensores = None
			Snackbar(text="Carga completada.").show()

	def getName(self):
		"""Retorna el nombre del piso."""
		return self.name

	def agregar_motas(self):
		"""Agrega las motas que se crearon al floatlayout."""
		for each in self.info_motas.items():
			self.flayout.add_widget(each[1])

	def procesar_datos(self):
		"""Crea las motas en base a lo que recibio al instanciarse el piso."""
		control = self.client.Mote.first_where(mote_id='linti_control')
		if control is None:
			# FIXME: Deberíamos tener algo más genérico
			raise Exception('No existe linti_control, pensar otra forma de implementar esto')

                historial = list(self.client.Measurement.where(mote_id='linti_control')) #NO DEVUELVE NADA

		temperature = historial[0].temperature if len(historial) > 0 else 0#float('nan')
		historial = historial if len(historial) > 0 else [0]
		#~ historial = [15]  #QUITAR HARDCODEO
		#~ self.info_motas[control.mote_id] = Mota(control, historial, temperature, self.client)
		self.info_motas[control.mote_id] = Mota(control, historial, historial[0], self.client)
		for sen in self.sensores:
			#~ print "\nProcesando un sensor\n"
			historial = list(self.client.Measurement.where(mota_id=sen.mote_id)) #NO DEVUELVE NADA
			#~ historial = self.client.Measurement.first_where(mota_id=sen.mote_id) #FIX ME
			historial = historial if len(historial) > 0 else [100]
			#~ historial = [25] #QUITAR HARDCODEO
			#~ print "\nSe cargo el historial\n"
			self.info_motas[sen.mote_id] = Mota(sen, historial, self.info_motas["linti_control"].getTemperatura(), self.client)
			#~ print "\nSe agrego la mota\n"

		self.ids['fecha'].text = 'Ultima actualización: '+datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y %H:%M')

	def actualizar_mapa(self):
		#FIXME: ADAPTAR A WENUCLIENT
		"""Deprecated (cambiar con wenuapi). Actualiza los valores/datos de las motas del piso."""
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
		"""Cambia de posicion las motas (FIXME)."""
		mfp = MakeFilePos(self.info_motas, self.client)
		self.add_widget(mfp)
		mfp.size = self.parent.size
		self.actualizar_mapa()


class MakeFilePos(Widget):
	"""Clase para modificar la posicion de las motas."""

	def __init__(self, motas, cli, *args):
		"""Crea una copia de las motas para cambiar su posicion."""
		super(MakeFilePos, self).__init__()
		self.motas = motas
		self.motas2 = motas.copy()
		self.client = cli
		self.m_pos = {}
		#~ self.size = Window.size
		self.size_hint_y= None
		self.size_hint_x= None
		#~ self.size = 900, 150
		self.pos = 0,0
		key = self.motas2.keys()[0]
		l = MDLabel(text="Ingrese posición de la mota: "+str(key), 
				pos_hint={'top':1.44,'right':.06})#,
				#~ font_style= 'Display1',
				#~ theme_text_color= 'Primary',
				#~ halign= 'center',
				#~ size_hint_y= None,
				#~ size_hint_x= None,
				#~ height= dp(4))
		#~ Snackbar(text="Ingrese posición de la mota: "+str(key)).show()
		self.add_widget(l)
		#del self.motas2[key]
		#~ self.size = self.parent.size

	def calc_pos(self, tx, ty, key):
		"""Calcula la nueva posicion."""
		pos = (tx-(self.motas[str(key)].size[0]/2),ty-(self.motas[str(key)].size[1]/2))
		return map(int, pos)

	def on_touch_down(self, touch):
		"""Con cada touch obtiene la posicion nueva de una mota y la quita de la lista."""
		if len(self.children) > 0:
			self.remove_widget(self.children[-1])
		if len(self.motas2) > 0:
			key = self.motas2.keys()[0]
			self.m_pos[str(key)] = self.calc_pos(touch.pos[0], touch.pos[1], key)
			del self.motas2[key]
			if len(self.motas2) > 0:
				key = self.motas2.keys()[0]
				l = MDLabel(text="Ingrese posición de la mota: "+str(key), 
						pos_hint={'top':1.44,'right':.06})#,
						#~ font_style= 'Display1',
						#~ theme_text_color= 'Primary',
						#~ halign= 'center',
						#~ size_hint_y= None,
						#~ size_hint_x= None,
						#~ height= dp(12))
				#~ Snackbar(text="Ingrese posición de la mota: "+str(key)).show()
				self.add_widget(l)
			else:
				l = MDLabel(text="Haga click para finalizar", pos_hint={'top':1.44,'right':.06})
				#~ Snackbar(text="Haga click para finalizar").show()
				self.add_widget(l)
		else:
			Snackbar(text="Espere un momento mientras se guardan las nuevas posiciones.").show()
			Clock.schedule_once(self.posicionar, .5)
		return True
		
	def posicionar(self, *evt):
		"""Actualiza la posicion de las motas en base a las nuevas ingresadas."""
		for m in self.motas.keys():
			mote = self.client.Mote.first_where(mote_id=m, level_id = self.motas[m].get_piso())
			mote.x = self.m_pos[m][0];
			mote.y = self.m_pos[m][1];
			mote.resolution = str(Window.size)
			mote.save()
			self.motas[str(m)].pos = self.motas[str(m)].pos = self.motas[str(m)].translate(self.motas[str(m)].orig_size, Window.size, self.m_pos[m][0],self.m_pos[m][1])
		self.parent.remove_widget(self)
		Snackbar(text="Posiciones guardadas.").show()
