# -*- coding: utf-8 -*-
import kivymd.snackbar as Snackbar
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.uix.button import Button
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

import os
import urllib
from piso import *
#influx
from influxdb import InfluxDBClient

class PisosNavDrawer(MDNavigationDrawer):
	pass

class MainBox(BoxLayout):
	theme_cls = ThemeManager()
	#theme_cls.theme_style = 'Dark'
	theme_cls.primary_palette = "Green"
	theme_cls.secondary_palette = "Blue"
	pisos_nav = ObjectProperty(None)
	#~ pisos_nav = PisosNavDrawer()
	lay_nav = ObjectProperty(None)
	#~ lay_nav = NavigationLayout()

	def __init__(self, *args, **kwargs):
		super(MainBox, self).__init__(**kwargs)
		self.icon = 'pin_1.png'
		self.title = 'Datos Sensores'
		print self.ids

		#~ self.nav_layout = self.ids["nav_layout"]
		#~ self.nav_drawer = self.ids["nav_drawer"]
		#~ self.nav_layout = NavigationLayout()
		#~ self.nav_drawer = PisosNavDrawer()
		#~ self.nav_drawer.add_widget(PisosNavDrawer())
		#~ self.nav_layout.add_widget(self.nav_drawer)
		self.pisos_nav.add_widget(NavigationDrawerIconButton(text="seee"))
		self.iniciar("bottomsheet","piso_1")

		self.menu_items = [
        {'viewclass': 'MDMenuItem',
         'text': 'Posicionar',
         'on_release': self.pos_motas},
        {'viewclass': 'MDMenuItem',
         'text': 'Actualizar'}#,
         #'on_release': self.cambiar_piso},
    	]

	def iniciar(self, actual_screen, next_screen):
		#if next_screen == "info":
			#Clock.schedule_interval(self.update, 0.5)
		print "inicia!"
		try:
			self.client = InfluxDBClient('influxdb.linti.unlp.edu.ar', 8086, "lihuen", '***REMOVED***', 'uso_racional')
			self.client.query('SELECT mota_id FROM medicion LIMIT 1') #por ahora la unica forma de testear la conexion.

		except Exception as e:
			print str(e)
			print("Error al efectuar la conexion")
			#popup = Popup(title='Error al conectarse', content=Label(text="Error de conexión.\nVerifique su conexión a internet y sus credenciales de acceso.\n\n\nPara cerrar el cuadro de diálogo presione fuera de este."), size_hint=(.8, .6))
			#popup.open()
		else:
			#instancio piso y paso el client - falta ahcer una consulta para saber cuantos pisos hay
			pisos = self.client.query('SELECT * FROM piso')
			print pisos.get_points().next()
			print "----------------------aaaaaaaaaaaaaaaaaaaa-------------------------------------"
			#p_imgs = ["imagenes/plano-2piso.jpg","imagenes/primer_piso.jpg"]
			#self.pisos = []
			self.pisos = {}
			#~ self.spinner = Spinner(text="1", size_hint= (.09,.05), pos_hint={'top':1,'left':.9})
			for pp in pisos:
				for p in pp:
					print "*************************************"
					print p
					print "**********************pppppp*********"
					#~ self.spinner.values.append(str(p))
					sensores = self.client.query("SELECT * FROM mota WHERE piso_id ='"+str(p["piso_id"])+"'")
					print sensores
					print "+++++++++++++++++++++++++****++++++++++++++++++++++++++++++"
					img = 'piso_'+str(p["piso_id"])+'.png'
					print img
					if ((not os.path.exists(img)) and (not os.path.exists("imagenes/"+img))):
						try:
							urllib.urlretrieve(str(p['mapa']),img)
						except Exception as e:
							print "Error al descargar la imagen del piso "+img+"\n"
							print e
					#~ else:
					print "pisoooosss"
					print p['piso_id']
					#self.pisos.append(Piso(p['piso_id'], sensores, img, self.client))
					self.pisos["piso_"+p['piso_id']] = Piso(p['piso_id'], sensores, img, self.client)
					self.pisos["piso_"+p['piso_id']].agregar_motas()
					p_nav = NavigationDrawerIconButton(text=self.pisos["piso_"+p['piso_id']].getName())
					p_nav.icon = "checkbox-blank-circle"
					p_nav.bind(on_release=partial(self.cambiar_piso, self.pisos["piso_"+p['piso_id']].getName()))
					self.pisos_nav.add_widget(p_nav)
					#self.main_widget.ids["scr_mngr"].add_widget(self.pisos[-1])
					self.ids["scr_mngr"].add_widget(self.pisos["piso_"+p['piso_id']])
			else:
				#self.main_widget.ids["scr_mngr"].current = next_screen
				self.ids["scr_mngr"].current = next_screen

	def cambiar_piso(self, name, evnt):
		#self.main_widget.ids["scr_mngr"].current = name
		self.ids["scr_mngr"].current = name

	"""def open_menu(self):
		print "Abre menu"
		m_item = MDMenuItem()
		#m_item.text = "ssdasld"
		MD = MDDropdownMenu(items=self.menu_items,width_mult=2)
		#MD.center_x =
		MD.open(self)"""

	def pos_motas(self):
		#print self.ids
		print self.ids["scr_mngr"].current
		self.pisos[self.ids["scr_mngr"].current].config_mota_pos()

class DatosSensoresApp(App):
	theme_cls = ThemeManager()
	#theme_cls.theme_style = 'Dark'
	theme_cls.primary_palette = "Green"
	theme_cls.secondary_palette = "Blue"
	#nav_drawer = ObjectProperty()

	def build(self):
		Builder.load_file('datosSensores.kv')
		return MainBox()


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
