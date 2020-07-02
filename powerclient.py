#!/usr/bin/env python

import time
import os
import sys
import struct
import json
import requests
import thread
from subprocess import Popen


### DECODE THE FLOATING POINT AS ENCODED IN BIG ENDIAN BY THE DTPOWER DAEMON
def decode_float(block):
	qword = int(struct.unpack('>q', block)[0])
	flt = float(qword)
	rnd = str(flt).split('.')
	tmp = rnd[0] + '.' + rnd[1][0]
	
	if len(rnd[1]) < 2:
		tmp+='0'
	else:
		tmp+=rnd[1][1]

	if len(rnd[1]) < 3:
		tmp+='0'
	else:
		tmp+=rnd[1][2]

		flt = tmp

	return tmp


## DTPOWER API
class DTPower(object):

	def __init__(self, host='localhost', port='7808'):
		self.api = 'http://'+host+':'+port+'/'
		#self.iproxy = Popen(["iproxy", "7808", "7808"])

	def GetSessionRecordingEnabled(self):
		f = requests.get(self.api+'control/sessionRecordingEnabled')
		return f.content == "YES"

	def GetRecordingOptions(self):
		f = requests.get(self.api+'control/recordingOptions')
		return f.content

	def EnableAllRecordings(self):
		rec = self.GetRecordingOptions()
		if rec:
			rec = rec.replace("false", "true")

		f = requests.put(self.api+'control/recordingOptions', data=rec)
		return f.content == "OK"

	def GetSession(self):
		f = requests.get(self.api+'session/index.plist')
		return f.content

	def SetSessionRecordingEnabled(self, toggle=1):
		if toggle == 1:
			toggle = "YES"
		else:
			toggle = "NO"
		f = requests.put(self.api+'control/sessionRecordingEnabled', data=toggle)
		return f.content == "OK"

	def ParseAppState(self):
		f = requests.get(self.api+'live/fgapp_change.dat', stream=True)
		for data in f.iter_content(chunk_size=1024):

			rows = data.split('AppState')

			for row in rows:
				columns = row.split('\t')
				if len(columns) != 6:
					continue
				columns[0] = 'AppState'
				columns[1] = int(columns[1])
				columns[2] = int(columns[2])

				print("%s\n---------------" % columns[4])
				print("process name: %s" % columns[3])
				print("process ID: %d" % columns[2])
				print("State: %d" % columns[1])
				print("Description: %s\n\n" % columns[5].split('@')[0])

	def ParseGPS(self):
		f = requests.get(self.api+'live/gps.dat', stream=True)
		for data in f.iter_content(chunk_size=9):

			idx = 0

			flt = decode_float(data[idx:idx+8])
			b = struct.unpack('c', data[idx+8:idx+9])[0] # Get the GPS state byte

			# Log it
			print('[T+'+flt+'] GPS State changed: %d' % ord(b))

	def ParseWiFi(self):
		f = requests.get(self.api+'live/wifi.dat', stream=True)
		for data in f.iter_content(chunk_size=9):

			idx = 0

			flt = decode_float(data[idx:idx+8])
			b = struct.unpack('c', data[idx+8:idx+9])[0] # Get the GPS state byte

			# Log it
			print('[T+'+flt+'] WiFi State changed: %d' % ord(b))

	def ParseBluetooth(self):
		f = requests.get(self.api+'live/bluetooth.dat', stream=True)
		for data in f.iter_content(chunk_size=9):

			idx = 0

			flt = decode_float(data[idx:idx+8])
			b = struct.unpack('c', data[idx+8:idx+9])[0] # Get the bluetooth state byte

			# Log it
			print('[T+'+flt+'] Bluetooth State changed: %d' % ord(b))


	def ParseBrightness(self):
		f = requests.get(self.api+'live/brightness.dat', stream=True)
		for data in f.iter_content(chunk_size=24):
			idx = 0
			t1 = decode_float(data[idx:idx+8])
			t2 = decode_float(data[idx+8:idx+16])
			brightness = decode_float(data[idx+16:idx+24])

			# Log it
			print('[T+'+t1+'/'+t2+'] Brightness changed: '+brightness)

	def ParseNetworkActivity(self):
		f = requests.get(self.api+'live/network_activity.dat', stream=True)
		for data in f.iter_content(chunk_size=24):
			if len(data) < 24:
				continue
			idx = 0
			t1 = decode_float(data[idx:idx+8])
			t2 = decode_float(data[idx+8:idx+16])
			netact = decode_float(data[idx+16:idx+24])

			# Log it
			print('[T+'+t1+'/'+t2+'] Network activity changed: '+netact)

	def ParsePowerSourceEvents(self):
		f = requests.get(self.api+'live/powersrc_events.dat', stream=True)
		for data in f.iter_content(chunk_size=100):
			idx = 0
			t1 = decode_float(data[idx:idx+8])

			# Log it
			print('[T+'+t1+'] Powersource changed: '+data[idx+9:len(data)-1])

	def ParseDTXLog(self):
		f = requests.get(self.api+'live/log.dtx', stream=True)
		for data in f.iter_content(chunk_size=1024):
			o = open('log.dtx', 'a')
			o.write(data)

		o.close()

power = DTPower()

def AppStateMonitor(threadName):
	try:
		power.ParseAppState()
	except Exception as ex:
#		print("[AppStateMonitor]: An exception occured: "+str(ex.message))
		time.sleep(1)
		AppStateMonitor(threadName)

def GPSMonitor(threadName):
	try:
		power.ParseGPS()
	except Exception as ex:
#		print("[GPSMonitor]: An exception occured: "+str(ex.message))
                time.sleep(1)
		GPSMonitor(threadName)

def BrightnessMonitor(threadName):
	try:
		power.ParseBrightness()
	except Exception as ex:
#		print("[BrightnessMonitor]: An exception occured: "+str(ex.message))
                time.sleep(1)
		BrightnessMonitor(threadName)

def WiFiMonitor(threadName):
	try:
		power.ParseWiFi()
	except Exception as ex:
		print("[WiFiMonitor]: An exception occured: "+str(ex.message))
                time.sleep(1)
		WiFiMonitor(threadName)

def BluetoothMonitor(threadName):
	try:
		power.ParseBluetooth()
	except Exception as ex:
#		print("[BlueToothMonitor]: An exception occured: "+str(ex.message))
                time.sleep(1)
		BluetoothMonitor(threadName)

def NetworkActivityMonitor(threadName):
	try:
		power.ParseNetworkActivity()
	except Exception as ex:
#		print("[NetworkActivityMonitor]: An exception occured: "+str(ex.message))
                time.sleep(1)
		NetworkActivityMonitor(threadName)

def PowerSourceEventMonitor(threadName):
	try:
		power.ParsePowerSourceEvents()
	except Exception as ex:
#		print("[PowerSourceEventMonitor]: An exception occured: "+str(ex.message))
                time.sleep(1)
		PowerSourceEventMonitor(threadName)

# Enable all available recordings
power.EnableAllRecordings()

# Enable session recording
power.SetSessionRecordingEnabled(1)

print(power.GetSession())

thread.start_new_thread(AppStateMonitor, ("AppStateMonitor",))
thread.start_new_thread(GPSMonitor, ("GPSMonitor",))
thread.start_new_thread(BrightnessMonitor, ("BrightnessMonitor",))
thread.start_new_thread(WiFiMonitor, ("WiFiMonitor",))
thread.start_new_thread(BluetoothMonitor, ("BluetoothMonitor",))
#thread.start_new_thread(NetworkActivityMonitor, ("NetworkActivityMonitor",))
thread.start_new_thread(PowerSourceEventMonitor, ("PowerSourceEventMonitor",))

power.ParseDTXLog()
