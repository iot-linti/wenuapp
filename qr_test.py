import kivy
kivy.require('1.4.0')
 
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock
from PIL import Image
import zbarlight

class MyApp(App):
	def doscreenshot(self,*largs):
		self.cam.export_to_png("qrtests.png")
		file_path = 'qrtests.png'
		with open(file_path, 'rb') as image_file:
			image = Image.open(image_file)
			image.load()
		codes = zbarlight.scan_codes('qrcode', image)
		print('QR codes: %s' % codes)
		if codes != None:
			self.check_qr.cancel()
 
	def build(self):
		camwidget = Widget()
		self.cam = Camera()
		self.cam=Camera(resolution=(640,480), size=(500,500), play=True)
		camwidget.add_widget(self.cam)
		self.check_qr = Clock.schedule_interval(self.doscreenshot, 1)
		 
		return camwidget

if __name__ == '__main__':
	MyApp().run()
