#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
#~ from kivy.uix.video import Video
#~ from kivy.uix.image import Image
from kivy.uix.image import AsyncImage
from kivy.clock import Clock

class MainBox(BoxLayout):
	def __init__(self, *args, **kwargs):
		super(MainBox, self).__init__(**kwargs)
		#~ video = Video(source='http://163.10.10.103', play=True)
		self.video = AsyncImage(source='http://lihuen:lihuen@163.10.10.103/cgi-bin/viewer/video.jpg', nocache=True)
		self.add_widget(self.video)
		Clock.schedule_interval(self.refresh, 1)
		
	def refresh(self, *evnt):
		print "reload"
		self.video.reload()

class VideoApp(App):

	def build(self):
		return MainBox()

if __name__ == '__main__':
	VideoApp().run()

