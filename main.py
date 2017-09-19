# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen

from kivymd.label import MDLabel
from kivymd.list import ILeftBody, ILeftBodyTouch, IRightBodyTouch
from kivymd.navigationdrawer import MDNavigationDrawer, NavigationLayout
from kivymd.selectioncontrols import MDCheckbox
from kivymd.theming import ThemeManager
from kivymd.dialog import MDDialog
from kivymd.time_picker import MDTimePicker
from kivymd.date_picker import MDDatePicker

from kivymd.menu import MDDropdownMenu
from kivymd.menu import MDMenuItem

from kivymd.toolbar import Toolbar

from kivymd.navigationdrawer import NavigationDrawerIconButton

#~ from kivymd.textfields.MDTextField import MDTextField
from kivymd.tabs import MDTabbedPanel
from kivymd.progressbar import MDProgressBar

from kivy.clock import Clock
from kivy.uix.camera import Camera

from kivy.utils import platform

import os
import urllib
from piso import *
from PIL import Image as ImagePil
if platform == 'android':
	try:
		from zbarQrCode import ZbarQrcodeDetector
	except Exception as e:
		print e
else:
	import zbarlight
#influx
#~ from influxdb import InfluxDBClient
import wenuclient
import requests

class PisosNavDrawer(MDNavigationDrawer):
	pass

class Login(MDTabbedPanel):
	"""Clase de inicio de sesion/coneccion al servidor de influx mediante wenuapi"""
	usr = ObjectProperty(None)
	password = ObjectProperty(None)
	server_ip = ObjectProperty(None)
	cam = None

	def conectar(self, user, password, server):
		"""Conecta al servidor"""
		config = App.get_running_app().config
		try:
			config.set('WENU', 'USER', user)
			config.set('WENU', 'PASS', password)
			config.set('WENU', 'SERVER', server)
			config.write()
			#~ server = config.get('WENU', 'SERVER')
			
                        session = wenuclient.get_session(
                            '/'.join((server, 'login')),
                            user,
                            password,
                        )
			self.parent.parent.client = wenuclient.Client(server, session)
		except requests.exceptions.RequestException as e:
			print e
			print("Error al efectuar la conexion")
			self.error_dialog("Error al conectar. Verifique el usuario y contraseña.")
		else:
			self.parent.parent.current = 'progressbar'
			#~ self.parent.parent.iniciar("bottomsheet","piso_1", self.client, self)
			#~ self.parent.parent.current = 'main'
			self.parent.remove_widget(self)
			
	def read_qr(self):
		"""Abre la camara para leer un codigo de QR"""
		self.content = Widget()
		if platform == 'android':
			self.detector = ZbarQrcodeDetector()
			self.detector.bind(symbols=self.connect_qr)
			self.content.add_widget(self.detector)
			#~ self.dialog = MDDialog(title="Enfoque el codigo QR",content=self.content, size_hint=(.8, None),height=dp(500),auto_dismiss=False)
			#~ self.dialog.add_action_button("Cerrar", action= lambda x: self.close_dialog())
			#~ self.dialog.open()
			self.detector.start()
		else:
			if self.cam == None:
				self.cam=Camera(resolution=(640,480), size=(400,400), play=True)
				#~ self.add_widget(self.cam)
			else:
				self.cam.play=True
			self.content.size_hint = None, None
			self.content.height = dp(400)
			self.content.add_widget(self.cam)
			self.check_qr = Clock.schedule_interval(self.detect_qr, 1)
		self.dialog = MDDialog(title="Enfoque el codigo QR",content=self.content, size_hint=(.8, None),height=dp(500),auto_dismiss=False)
		self.dialog.add_action_button("Cerrar", action= lambda x: self.close_dialog())
		self.dialog.open()
		
	def close_dialog(self):
		self.dialog.dismiss()
		if platform == 'android':
			self.detector.stop()
			self.content.remove_widget(self.detector)
		
	def connect_qr(self, *args):#, token):
		if platform == 'android':
			self.detector.stop()
			try:
				token = self.detector.symbols[0][1]
			except IndexError:
				print self.detector.symbols
				token = []
			print token
		else:
			token = args[0]
		self.dialog.dismiss()
		try:
			session = wenuclient.get_session_by_qr(token)
			self.parent.parent.client = wenuclient.Client(self.server_ip.text, session)
		except requests.exceptions.RequestException as e:
			print("Error al efectuar la conexion")
			self.error_dialog("Token incorrecto")
		else:
			self.parent.parent.current = 'progressbar'
			a = open('token.txt','w')
			a.write(token)
			a.write(self.server_ip.text)
			a.close()
			#~ self.parent.parent.iniciar("bottomsheet","piso_1", self.client, self)
			#~ self.parent.parent.current = 'main'
			self.parent.remove_widget(self)
		
		
		
	def detect_qr(self,*largs):
		self.cam.export_to_png("qrtests.png")
		file_path = 'qrtests.png'
		with open(file_path, 'rb') as image_file:
			image = ImagePil.open(image_file)
			image.load()
		codes = zbarlight.scan_codes('qrcode', image)
		print('QR codes: %s' % codes)
		if codes != None:
			self.dialog.dismiss()
			self.check_qr.cancel()
			self.content.remove_widget(self.cam)
			self.remove_widget(self.content)
			self.cam.play = False
			self.connect_qr(codes[0])

	def error_dialog(self, txt):
		"""Muestra un dialogo de error en caso de no poder conectarse."""
		content = MDLabel(font_style='Body1',theme_text_color='Secondary', text=txt, size_hint_y=None, valign='top')
		content.bind(texture_size=content.setter('size'))
		self.dialog = MDDialog(title="Error",content=content, size_hint=(.8, None),height=dp(200),auto_dismiss=False)
		self.dialog.add_action_button("Cerrar", action=lambda x: self.dialog.dismiss())
		self.dialog.open()
		
	

class Load(Screen):
	"""Clase de progressbar mientras se cargan los pisos."""
	prog_b = ObjectProperty(None)
	
	def __init__(self, *args, **kwargs):
		super(Load, self).__init__(**kwargs)
		#~ print "PROGREEESSS"
		#~ self.parent.iniciar("bottomsheet","piso_1", self)
		#~ self.cargar()
		
	def on_enter(self, *args):
		#~ print "enter"
		self.parent.iniciar("bottomsheet","piso_1")
		
	def update(self, cant=10, sig=0, *args):
		self.prog_b.value += 100 / cant
		self.parent.iniciar("bottomsheet","piso_1",+ sig)

class MainBox(ScreenManager):
	"""Clase principal que contiene el primer screen manager."""
	pisos_nav = ObjectProperty(None)

	def __init__(self, config, *args, **kwargs):
		super(MainBox, self).__init__(**kwargs)
		#~ super(MainBox, self).__init__(client, **kwargs)
		self.icon = 'pin_1.png'
		self.title = 'Datos Sensores'
		#~ self.client = client
		self.client = None
		self.pisos = {}

		self.config = config

		self.menu_items = [
        {'viewclass': 'MDMenuItem',
         'text': 'Posicionar',
         'on_release': self.pos_motas},
        {'viewclass': 'MDMenuItem',
         'text': 'Actualizar'}#,
         #'on_release': self.cambiar_piso},
         	]
		
		if os.path.isfile('token.txt'):
			t = open('token.txt','r')
			token, ip = t.readlines()
			print token, ip
			#El siguiente codigo empieza a repetirse un par de veces (creo)-> refactorizar (?).
			try:
				session = wenuclient.get_session_by_qr(token)
				print session
				print session.auth
				print session.get(ip)
				self.client = wenuclient.Client(ip, session)
			except requests.exceptions.RequestException as e:
				print("Error al efectuar la conexion")
				print e
				#~ self.error_dialog("Token incorrecto")
				
				#~ content = MDLabel(font_style='Body1',theme_text_color='Secondary', text="Token expirado o incorrecto.", size_hint_y=None, valign='top')
				#~ content.bind(texture_size=content.setter('size'))
				#~ self.dialog = MDDialog(title="Error",content=content, size_hint=(.8, None),height=dp(200),auto_dismiss=False)
				#~ self.dialog.add_action_button("Cerrar", action=lambda x: self.dialog.dismiss())
				#~ self.dialog.open()
				#No lo muestra por alguna razon.
				
				self.current = 'login'
			#
			else:
				self.current = 'progressbar'
		else:
			self.current = 'login'

	def log(self):
		"""Cambia al screen de login."""
		#~ print self.ids
		self.ids["smp"].current = 'login'

	def iniciar(self, actual_screen, next_screen, sig=0):
		"""Crea un piso a la vez. Cuando creó todos pasa al siguiente screen."""
		cant_p = len(self.client.Level.list())
		#~ for piso in self.client.Level.list():
		#-------------------------------------------------------------------------#
		if sig < cant_p:
			#~ print "before"
			piso = self.client.Level.list()[sig]
			sensores = self.client.Mote.where(level_id=piso._id)
			#~ print "after"
			sensores = list(sensores)
			img = 'imagenes/piso_'+str(piso._id)+'.png'
			#~ print img
			if (not os.path.exists(img)):
				try:
					urllib.urlretrieve(str(piso.map),img)
				except Exception as e:
					print "Error al descargar la imagen del piso "+img+"\n"
					print e
			#~ print piso._id
			self.pisos[piso._id] = Piso(piso._id, sensores, img, self.client)
			self.pisos[piso._id].agregar_motas()
			p_nav = NavigationDrawerIconButton(text=self.pisos[piso._id].getName())
			p_nav.icon = "checkbox-blank-circle"
			p_nav.bind(on_release=partial(self.cambiar_piso, self.pisos[piso._id].getName()))

			self.pisos_nav.add_widget(p_nav)
			self.ids["scr_mngr"].add_widget(self.pisos[piso._id])
			#~ print "Piso listo"
			Clock.schedule_once(partial(self.ids["progressbar"].update, cant_p, sig+1), .1)
		else:
			self.ids["scr_mngr"].current = next_screen
			self.current = 'main'
			self.pisos[1].on_enter()

	def cambiar_piso(self, name, evnt):
		"""Cambia de piso (Screen)"""
		self.ids["scr_mngr"].current = name

	def pos_motas(self):
		"""Ubica las motas en el piso."""
		piso_id = int(self.ids["scr_mngr"].current.split('_')[-1])
		#~ print piso_id
		#~ print self.pisos.keys()
		self.pisos[piso_id].config_mota_pos()

class LoginScreen(Screen):
	pass

class DatosSensoresApp(App):
	theme_cls = ThemeManager()
	#theme_cls.theme_style = 'Dark'
	theme_cls.primary_palette = "Green"
	theme_cls.secondary_palette = "Blue"
	#nav_drawer = ObjectProperty()

	def build(self):
		self.configuration = self.config
		Builder.load_file('datosSensores.kv')
		self.mb = MainBox(self.config)
		return self.mb

	########################################################################
	def build_config(self, config):
		config.setdefaults('WENU', {
			'SERVER': 'http://localhost:5000',
			'USER': 'admin',
			'PASS': 'wenu',
		})


	def on_pause(self):
		if platform == 'android':
			from android import AndroidService
			service = AndroidService('Datos Sensores', 'running')
			service.start('service started')
			self.service = service
		return True
	
	def on_resume(self):
		self.service.stop()
		self.service = None
########################################################################

if __name__ == '__main__':
	DatosSensoresApp().run()
