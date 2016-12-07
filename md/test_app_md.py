# -*- coding: utf-8 -*-
import kivymd.snackbar as Snackbar
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivymd.bottomsheet import MDListBottomSheet, MDGridBottomSheet
from kivymd.button import MDIconButton
from kivymd.label import MDLabel
from kivymd.list import ILeftBody, ILeftBodyTouch, IRightBodyTouch
from kivymd.navigationdrawer import NavigationDrawer
from kivymd.selectioncontrols import MDCheckbox
from kivymd.theming import ThemeManager
from kivymd.dialog import MDDialog
from kivymd.time_picker import MDTimePicker
from kivymd.date_picker import MDDatePicker

from kivymd.navigationdrawer import NavigationDrawerIconButton

import os
import urllib
from piso import *
#influx
from influxdb import InfluxDBClient

main_widget_kv = '''
#:import Toolbar kivymd.toolbar.Toolbar
#:import ThemeManager kivymd.theming.ThemeManager
#:import NavigationDrawer kivymd.navigationdrawer.NavigationDrawer
#:import MDCheckbox kivymd.selectioncontrols.MDCheckbox
#:import MDSwitch kivymd.selectioncontrols.MDSwitch
#:import MDList kivymd.list.MDList
#:import OneLineListItem kivymd.list.OneLineListItem
#:import TwoLineListItem kivymd.list.TwoLineListItem
#:import ThreeLineListItem kivymd.list.ThreeLineListItem
#:import OneLineAvatarListItem kivymd.list.OneLineAvatarListItem
#:import OneLineIconListItem kivymd.list.OneLineIconListItem
#:import OneLineAvatarIconListItem kivymd.list.OneLineAvatarIconListItem
#:import SingleLineTextField kivymd.textfields.SingleLineTextField
#:import MDSpinner kivymd.spinner.MDSpinner
#:import MDCard kivymd.card.MDCard
#:import MDSeparator kivymd.card.MDSeparator

#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import colors kivymd.color_definitions.colors
#:import SmartTile kivymd.grid.SmartTile
#:import MDSlider kivymd.slider.MDSlider
#:import MDTabbedPanel kivymd.tabs.MDTabbedPanel
#:import MDTab kivymd.tabs.MDTab
#:import MDProgressBar kivymd.progressbar.MDProgressBar
#:import MDAccordion kivymd.accordion.MDAccordion
#:import MDAccordionItem kivymd.accordion.MDAccordionItem
#:import MDThemePicker kivymd.theme_picker.MDThemePicker

BoxLayout:
	orientation: 'vertical'
	Toolbar:
		id: toolbar
		title: 'Datos sensores'
		background_color: app.theme_cls.primary_color
		left_action_items: [['menu', lambda x: app.nav_drawer.toggle()]]
		right_action_items: [['dots-vertical', lambda x: app.nav_drawer.toggle()]]
	ScreenManager:
		id: scr_mngr
		Screen:
			name: 'bottomsheet'
			MDRaisedButton:
				text: "Open list bottom sheet"
				opposite_colors: True
				size_hint: None, None
				size: 4 * dp(48), dp(48)
				pos_hint: {'center_x': 0.5, 'center_y': 0.6}
				on_release: app.show_example_bottom_sheet()
			MDRaisedButton:
				text: "Open grid bottom sheet"
				opposite_colors: True
				size_hint: None, None
				size: 4 * dp(48), dp(48)
				pos_hint: {'center_x': 0.5, 'center_y': 0.3}
				on_release: app.show_example_grid_bottom_sheet()
<KitchenSinkNavDrawer>
	title: "Pisos"
	id: pisos
	#NavigationDrawerIconButton:
	#	icon: 'checkbox-blank-circle'
	#	text: "Bottom"
	#	on_release: app.root.ids.scr_mngr.current = ''
	#NavigationDrawerIconButton:
	#	icon: 'checkbox-blank-circle'
	#	text: "Buttons"
	#	on_release: app.root.ids.scr_mngr.current = ''

<NavigationDraweIconButton>:
	icon: 'checkbox-blank-circle'

#
<Mota>:
	background_color: [0.0, 0.0, 0.0, 0.0]
	size_hint: (0.1, .1)
	markup: True
	valign: 'bottom'

<Piso>:
	flayout: flayout_id
	title_color: [ 33/255., 150/255., 243/255., .9 ]
	background: 'atlas:/data/images/defaulttheme/button_pressed'
	FloatLayout:
		id: flayout_id
		size: self.parent.size
		Label:
			id: fecha
			size_hint: (0.8, .1)
			pos_hint: {'top': 1.01, 'right': .6}
			text: 'Ultima actualización: '
			markup: True
		Button:
			id: actualizar
			size_hint: .09,.05
			#height: 30
			pos_hint: {'bottom':1,'right':.1}
			text: 'Actualizar'
			on_press: root.actualizar_mapa()
		Button:
			id: config_mota_pos
			size_hint: .09,.05
			pos_hint: {'bottom':.2,'right':.1}
			text: 'Posicionar'
			on_press: root.config_mota_pos()
'''

class KitchenSinkNavDrawer(NavigationDrawer):
	pass

class KitchenSink(App):
	theme_cls = ThemeManager()
	#theme_cls.theme_style = 'Dark'
	theme_cls.primary_palette = "Green"
	theme_cls.secondary_palette = "Blue"
	nav_drawer = ObjectProperty()

	def build(self):
		self.main_widget = Builder.load_string(main_widget_kv)
		# self.theme_cls.theme_style = 'Dark'

		#~ main_widget.ids.text_field_error.bind(
			#~ on_text_validate=self.set_error_message,
			#~ on_focus=self.set_error_message)

		self.nav_drawer = KitchenSinkNavDrawer()
		self.nav_drawer.add_widget(NavigationDrawerIconButton(text="seee"))
		self.iniciar("bottomsheet","piso_1")
		return self.main_widget


	########################################################################
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
			self.pisos = []
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
					print pisos
					self.pisos.append(Piso(p['piso_id'], sensores, img, self.client))
					self.pisos[-1].agregar_motas()
					p_nav = NavigationDrawerIconButton(text=self.pisos[-1].getName())
					p_nav.icon = "checkbox-blank-circle"
					p_nav.bind(on_release=partial(self.cambiar_piso, self.pisos[-1].getName()))
					self.nav_drawer.add_widget(p_nav)
					self.main_widget.ids["scr_mngr"].add_widget(self.pisos[-1])
			else:
				self.main_widget.ids["scr_mngr"].current = next_screen

	def cambiar_piso(self, name, evnt):
		self.main_widget.ids["scr_mngr"].current = name

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
	KitchenSink().run()