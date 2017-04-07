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

from kivymd.bottomsheet import MDListBottomSheet, MDGridBottomSheet
from kivymd.button import MDIconButton
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

import os
import urllib
from piso import *
#influx
from influxdb import InfluxDBClient

class PisosNavDrawer(MDNavigationDrawer):
	pass

class Login(BoxLayout):

	def conectar(self,usrer, password):
		#~ usr = self.parent.ids["usr"].text
		#~ passwd = self.parent.ids["password"].text
		usr = usrer
		passwd = password
		try:
			self.client = InfluxDBClient('influxdb.linti.unlp.edu.ar', 8086, usr, passwd, 'uso_racional')
			self.client.query('SELECT mota_id FROM medicion LIMIT 1') #por ahora la unica forma de testear la conexion.
		except Exception as e:
			print("Error al efectuar la conexion")
			self.error_dialog()
			#popup = Popup(title='Error al conectarse', content=Label(text="Error de conexión.\nVerifique su conexión a internet y sus credenciales de acceso.\n\n\nPara cerrar el cuadro de diálogo presione fuera de este."), size_hint=(.8, .6))
			#popup.open()
		else:
			#~ print self.root
			#~ print self.root.ids
			#~ self.parent.ids["mainbox"].iniciar(self.client)
			#~ self.parent.clear_widgets()
			mb = MainBox(client=self.client)
			print mb
			print "funciono???"
			print self.parent
			#~ self.parent.add_widget(mb)
			#~ self.parent.add(mb)
			#~ print "kdkkdfj"
			self.parent.current = 'main'
			self.parent.parent.iniciar("bottomsheet","piso_1", self.client)
			self.parent.remove_widget(self)
			#~ self.parent.remove(self)
			#~ self.add_widget(MainBox(client=self.client))
			#~ self.root = MainBox(client=self.client)
			#~ self.root = MainBox()
			#~ self.ids["scr_sm_log"].current = "sm_mb"

	def error_dialog(self):
		content = MDLabel(font_style='Body1',theme_text_color='Secondary', text="Error al conectar. Verifique el usuario y contraseña.", size_hint_y=None, valign='top')
		content.bind(texture_size=content.setter('size'))
		self.dialog = MDDialog(title="Error",content=content, size_hint=(.8, None),height=dp(200),auto_dismiss=False)
		self.dialog.add_action_button("Cerrar", action=lambda x: self.dialog.dismiss())
		self.dialog.open()

class MainBox(ScreenManager):
	theme_cls = ThemeManager()
	#theme_cls.theme_style = 'Dark'
	theme_cls.primary_palette = "Green"
	theme_cls.secondary_palette = "Blue"
	pisos_nav = ObjectProperty(None)
	#~ lay_nav = ObjectProperty(None)

	#~ def __init__(self, client, *args, **kwargs):
	def __init__(self, *args, **kwargs):
		super(MainBox, self).__init__(**kwargs)
		#~ super(MainBox, self).__init__(client, **kwargs)
		self.icon = 'pin_1.png'
		self.title = 'Datos Sensores'
		#~ self.client = client
		self.client = None

		#~ self.pisos_nav.add_widget(NavigationDrawerIconButton(text="seee"))
		#~ self.iniciar("bottomsheet","piso_1")

		self.menu_items = [
        {'viewclass': 'MDMenuItem',
         'text': 'Posicionar',
         'on_release': self.pos_motas},
        {'viewclass': 'MDMenuItem',
         'text': 'Actualizar'}#,
         #'on_release': self.cambiar_piso},
         	]
		#~ self.log()
		print "sssssssss"
		self.current = 'login'
		print "aaaaaaaaa"

	def log(self):
		print self.ids
		self.ids["smp"].current = 'login'

	def iniciar(self, actual_screen, next_screen, client):
		self.client = client
		#if next_screen == "info":
			#Clock.schedule_interval(self.update, 0.5)
		"""try:
			self.client = InfluxDBClient('influxdb.linti.unlp.edu.ar', 8086, "lihuen", '***REMOVED***', 'uso_racional')
			self.client.query('SELECT mota_id FROM medicion LIMIT 1') #por ahora la unica forma de testear la conexion.
		except Exception as e:
			print("Error al efectuar la conexion", e)
			#popup = Popup(title='Error al conectarse', content=Label(text="Error de conexión.\nVerifique su conexión a internet y sus credenciales de acceso.\n\n\nPara cerrar el cuadro de diálogo presione fuera de este."), size_hint=(.8, .6))
			#popup.open()
		else:"""
			#instancio piso y paso el client - falta ahcer una consulta para saber cuantos pisos hay
		pisos = self.client.query('SELECT * FROM piso')
		self.pisos = {}
		for pp in pisos:
			for p in pp:
				sensores = self.client.query("SELECT * FROM mota WHERE piso_id ='"+str(p["piso_id"])+"'")
				img = 'piso_'+str(p["piso_id"])+'.png'
				if ((not os.path.exists(img)) and (not os.path.exists("imagenes/"+img))):
					try:
						urllib.urlretrieve(str(p['mapa']),img)
					except Exception as e:
						print "Error al descargar la imagen del piso "+img+"\n"
						print e
				self.pisos["piso_"+p['piso_id']] = Piso(p['piso_id'], sensores, img, self.client)
				self.pisos["piso_"+p['piso_id']].agregar_motas()
				p_nav = NavigationDrawerIconButton(text=self.pisos["piso_"+p['piso_id']].getName().replace('_',' '))
				p_nav.icon = "checkbox-blank-circle"
				p_nav.bind(on_release=partial(self.cambiar_piso, self.pisos["piso_"+p['piso_id']].getName()))
				self.pisos_nav.add_widget(p_nav)
				self.ids["scr_mngr"].add_widget(self.pisos["piso_"+p['piso_id']])
		else:
			self.ids["scr_mngr"].current = next_screen

	def cambiar_piso(self, name, evnt):
		self.ids["scr_mngr"].current = name

	def pos_motas(self):
		self.pisos[self.ids["scr_mngr"].current].config_mota_pos()

class LoginScreen(Screen):
	pass

class BL(BoxLayout):

	def add(self, otro):
		self.add_widget(otro)

	def remove(self, otro):
		self.remove_widget(otro)

class DatosSensoresApp(App):
	theme_cls = ThemeManager()
	#theme_cls.theme_style = 'Dark'
	theme_cls.primary_palette = "Green"
	theme_cls.secondary_palette = "Blue"
	#nav_drawer = ObjectProperty()

	def build(self):
		Builder.load_file('datosSensores.kv')
		return MainBox()
		#~ bl = BL()
		#~ bl.add_widget(Login())
		#~ return Login()
		#~ return bl
		#~ sm = ScreenManager()
		#~ sm.add_widget(LoginScreen())
		#~ sm = self.ids["sm_log"]
		#~ return sm


	########################################################################


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
