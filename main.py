# -*- coding: utf-8 -*-
import kivymd.snackbar as Snackbar
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.uix.button import Button
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

from kivymd.progressbar import MDProgressBar

from kivy.clock import Clock

import os
import urllib
from piso import *
import time
import threading
#influx
from influxdb import InfluxDBClient
import wenuclient
import requests

class PisosNavDrawer(MDNavigationDrawer):
	pass

class Login(BoxLayout):

	def conectar(self, user, password):
		config = App.get_running_app().config
		try:
			config.set('WENU', 'USER', user)
			config.set('WENU', 'PASS', password)
			config.write()
			server = config.get('WENU', 'SERVER')
			
			session = requests.Session()
			session.auth = (user, password)
			self.parent.parent.client = wenuclient.Client(server, session)
		except requests.exceptions.RequestException as e:
			print("Error al efectuar la conexion")
			self.error_dialog()
		else:
			self.parent.parent.current = 'progressbar'
			#~ self.parent.parent.iniciar("bottomsheet","piso_1", self.client, self)
			#~ self.parent.parent.current = 'main'
			self.parent.remove_widget(self)

	def error_dialog(self):
		content = MDLabel(font_style='Body1',theme_text_color='Secondary', text="Error al conectar. Verifique el usuario y contraseña.", size_hint_y=None, valign='top')
		content.bind(texture_size=content.setter('size'))
		self.dialog = MDDialog(title="Error",content=content, size_hint=(.8, None),height=dp(200),auto_dismiss=False)
		self.dialog.add_action_button("Cerrar", action=lambda x: self.dialog.dismiss())
		self.dialog.open()

class Load(Screen):
	prog_b = ObjectProperty(None)
	
	def __init__(self, *args, **kwargs):
		super(Load, self).__init__(**kwargs)
		#~ print "PROGREEESSS"
		#~ self.parent.iniciar("bottomsheet","piso_1", self)
		#~ self.cargar()
		
	def on_enter(self, *args):
		print "enter"
		self.parent.iniciar("bottomsheet","piso_1")
		
	def update(self, cant=10, sig=0):
		print "cant"
		print cant
		print 100 / cant
		print self.prog_b.value + 100 / cant
		self.prog_b.value += 100 / cant
		self.parent.iniciar("bottomsheet","piso_1", sig)

class MainBox(ScreenManager):
	theme_cls = ThemeManager()
	#theme_cls.theme_style = 'Dark'
	theme_cls.primary_palette = "Green"
	theme_cls.secondary_palette = "Blue"
	pisos_nav = ObjectProperty(None)

	def __init__(self, config, *args, **kwargs):
		super(MainBox, self).__init__(**kwargs)
		#~ super(MainBox, self).__init__(client, **kwargs)
		self.icon = 'pin_1.png'
		self.title = 'Datos Sensores'
		#~ self.client = client
		self.client = None

		self.config = config

		self.menu_items = [
        {'viewclass': 'MDMenuItem',
         'text': 'Posicionar',
         'on_release': self.pos_motas},
        {'viewclass': 'MDMenuItem',
         'text': 'Actualizar'}#,
         #'on_release': self.cambiar_piso},
         	]

		self.current = 'login'

	def log(self):
		print self.ids
		self.ids["smp"].current = 'login'

	def iniciar(self, actual_screen, next_screen, sig=0):
		#~ self.client = client
		#~ self.parent.remove_widget(login_widget)
		#~ self.current = "progressbar"
		#if next_screen == "info":
			#Clock.schedule_interval(self.update, 0.5)

		#instancio piso y paso el client - falta ahcer una consulta para saber cuantos pisos hay
		# pisos = self.client.query('SELECT * FROM piso')
		# print pisos.get_points().next()
		print "----------------------aaaaaaaaaaaaaaaaaaaa-------------------------------------"
		#p_imgs = ["imagenes/plano-2piso.jpg","imagenes/primer_piso.jpg"]
		self.pisos = {}
		#~ self.spinner = Spinner(text="1", size_hint= (.09,.05), pos_hint={'top':1,'left':.9})
		#~ self.add_widget(MDProgressBar())
		#~ self.ids["scr_mngr"].current = next_screen
		cant_p = len(self.client.Level.list())
		#~ for piso in self.client.Level.list():
		#-------------------------------------------------------------------------#
		if sig != len(self.client.Level.list()):
			#~ print "before"
			piso = self.client.Level.list()[sig]
			sensores = self.client.Mote.where(level_id=piso._id)
			#~ print "after"
			sensores = list(sensores)
			img = 'imagenes/piso_'+str(piso._id)+'.png'
			print img
			if (not os.path.exists(img)):
				try:
					urllib.urlretrieve(str(piso.map),img)
				except Exception as e:
					print "Error al descargar la imagen del piso "+img+"\n"
					print e
			#~ else:
			#~ print "pisoooosss"
			print piso._id
			self.pisos[piso._id] = Piso(piso._id, sensores, img, self.client)
			#~ print "Se creo el piso"
			self.pisos[piso._id].agregar_motas()
			#~ print "Se agregaron las motas al piso"
			p_nav = NavigationDrawerIconButton(text=self.pisos[piso._id].getName())
			p_nav.icon = "checkbox-blank-circle"
			p_nav.bind(on_release=partial(self.cambiar_piso, self.pisos[piso._id].getName()))
			#self.nav_drawer.add_widget(p_nav)
			self.pisos_nav.add_widget(p_nav)
			#self.main_widget.ids["scr_mngr"].add_widget(self.pisos[-1])
			self.ids["scr_mngr"].add_widget(self.pisos[piso._id])
			#~ self.ids["progressbar"].update(cant_p, sig+1)
			print "Piso listo"
		else:
			self.ids["scr_mngr"].current = next_screen
		self.ids["progressbar"].update(cant_p, sig+1)
		#~ time.sleep(2)
		#~ self.current = 'main'

	def cambiar_piso(self, name, evnt):
		self.ids["scr_mngr"].current = name

	def pos_motas(self):
		piso_id = int(self.ids["scr_mngr"].current.split('_')[-1])
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
		return MainBox(self.config)

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
			#~ #~
	def on_resume(self):
		self.service.stop()
		self.service = None
########################################################################

if __name__ == '__main__':
	DatosSensoresApp().run()
