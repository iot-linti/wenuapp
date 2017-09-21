#!/usr/bin/env python
# -*- coding: utf-8 -*-

#android
from plyer import notification
#kivy
#~ from kivy.core.audio import SoundLoader
#~ from kivy.clock import Clock
#wenuapi
import wenuclient
#python
import time
import datetime

def conexion():
	try:
		datos = open('token.txt','r')
	except IOError:
		print 'Error al abrir el archivo del token'
	else:
		token, ip = datos.readlines()
		try:
			session = wenuclient.get_session_by_qr(token[-1])
			self.parent.parent.client = wenuclient.Client(ip[-1], session)
		except requests.exceptions.RequestException as e:
			print "Error de conexion."

def leer_datos_motas(cli, ctrl):
	#Cambiar para monitorear las alertas.
	
	alertas = self.client.Alerta.where(resuelta=False)
	for a in alertas:
		if (a.time.today()+datetime.timedelta(days=1)) <= (a.time.today() - datetime.datetime.now()):
			notification.notify(app_name='Datos sensores', title=a.algo,message=' temperatura demasiado alta - '+str(a['temperature'])+'C')
		#marcar la alerta como vista? que se marque sola despues de un tiempo predefinido?


if __name__ == '__main__':
	con = conexion()
	print con
	if con:
		while True:
			leer_datos_motas(con, 'linti_control')
			time.sleep(1) #cambiar por el tiempo de actualizacion de las motas en la bd
			print "time"
