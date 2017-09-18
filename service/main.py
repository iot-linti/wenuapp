#!/usr/bin/env python
# -*- coding: utf-8 -*-

#android
from plyer import notification
#kivy
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
#wenuapi
import wenuclient
#python
import time

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
	motas = cli.Mote.list()
	control = cli.Mote.first_where(mote_id='linti_control')
	control_temp = cli.Measurement.first_where(mote_id=mote_id)
	try:
		for m in motas:
			mota = cli.Mote.first_where(mote_id=m.mote_id)
			measure = cli.Measurement.first_where(mote_id=mota.mote_id)
			if (measure['temperature'] > 1000):
				notification.notify(app_name='Datos sensores - medición', title=m.mote_id,message='Low battery')
				time.sleep(1)
			elif (measure['temperature'] > (control['temperature'] + 5)):
				notification.notify(app_name='Datos sensores - medición', title=m.mote_id,message=' esta overheating - '+str(m['temperature'])+'C')
				time.sleep(1)
			#~ else:
				#~ notification.notify('InfluxDB', mota.items()[0][1].next()['mota_id']+' todo OK - '+str(mota.items()[0][1].next()['temperatura'])+'C')
		#~ notification.notify('influxdb', 'anda semi-bien')
	except Exception as e:
		print e
		notification.notify('influxError',str(e))
	#~ notification.notify('llama','leer')


if __name__ == '__main__':
	con = conexion()
	print con
	if con:
		while True:
			leer_datos_motas(con, 'linti_control')
			time.sleep(1) #cambiar por el tiempo de actualizacion de las motas en la bd
			print "time"
