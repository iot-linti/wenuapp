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
				print m_id
				print m_id[1]
				mota = cli.query("SELECT * FROM medicion WHERE mota_id = '"+m_id[1]+"' ORDER BY time desc LIMIT 1")
				if (mota.items()[0][1].next()['temeratura'] > (control['temperatura'] + 5)):
					notification.notify('InfluxDB', mota['mota_id']+' esta overheating -'+mota['temperatura']+'C')
				else:
					notification.notify('InfluxDB', m_id['mota_id']+' todo OK -'+mota['temperature']+'C')
		#~ notification.notify('influxdb', 'anda semi-bien')
	except Exception as e:
		print e
		notification.notify('influxError','aksdjlkasjdaskdjksd'+str(e))
	notification.notify('llama','leer')


if __name__ == '__main__':
	con = conexion()
	print con
	if con:
		print "entro"
		while True:
			leer_datos_motas(con, 'linti_control')
			time.sleep(1)
			print "time"
