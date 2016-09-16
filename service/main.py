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
		return cliente
	except:
		notification.notify('InfluxDB', description + ' Error de conexión')

def leer_datos_motas(cli, ctrl):
	query = "SELECT temperature FROM climatizacion WHERE mote_id = '"+ctrl+"' ORDER BY time desc LIMIT 1"
	control = self.client.query(query).items()[0][1].next()

	motas_ids = client.query("SELECT DISTINCT(mote_id) FROM climatizacion")

	for mid in motas_ids:
		for m_id in mid:
			print m_id
			mota = client.query("SELECT mote_id, temperature, time FROM climatizacion WHERE mote_id = '"+m_id+"' ORDER BY time desc LIMIT 1")
			if (mota.items()[0][1].next()['temerature'] > (control['temperature'] + 5)):
				notification.notify('InfluxDB', description + m_id['mote_id']+' esta overheating -'+m_id['temperature']+'°C')


if __name__ == '__main__':
	con = conexion()
	print con
	if con:
		print "entro"
		while True:
			leer_datos_motas(con, 'linti_control')
			time.sleep(1)
			print "time"
