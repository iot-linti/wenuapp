#!/usr/bin/env python
# -*- coding: utf-8 -*-

#android
from plyer import notification
#kivy
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
#influx
from influxdb import InfluxDBClient
#python
import time

def conexion():
	try:
		client = InfluxDBClient('influxdb.linti.unlp.edu.ar', 8086, "lihuen", "***REMOVED***", 'uso_racional')
		return client
	except Exception as e:
		notification.notify('InfluxDB', ' Error de conexion '+str(e))

def leer_datos_motas(cli, ctrl):
	query = "SELECT temperatura FROM medicion WHERE mota_id = '"+ctrl+"' ORDER BY time desc LIMIT 1"
	control = cli.query(query).items()[0][1].next()

	motas_ids = cli.query("SELECT x, mota_id FROM mota")

	try:
		for mid in motas_ids:
			for m_id in mid:
				mota = cli.query("SELECT * FROM medicion WHERE mota_id = '"+m_id["mota_id"]+"' ORDER BY time desc LIMIT 1")
				m = mota.items()[0][1].next()
				if (m['temperatura'] > 1000):
					notification.notify(app_name='Datos sensores - medición', title=m['mota_id'],message='Low battery')
					time.sleep(1)
				elif (m['temperatura'] > (control['temperatura'] + 5)):
					notification.notify(app_name='Datos sensores - medición', title=m['mota_id'],message=' esta overheating - '+str(m['temperatura'])+'C')
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
			time.sleep(1)
			print "time"
