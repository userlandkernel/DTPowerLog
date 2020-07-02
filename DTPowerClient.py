#!/usr/bin/env python
# Proprietary and confidential property of PhoneCheck LLC
# Written by Sem Voigtlander <sem@phonecheck.com>

## USAGE:
## Mount developer disk image with ideviceimagemounter
## iproxy 7808 7808
## Now you can use this script

import os
import sys
import struct
import socket
from pwn import *

class SessionReplayer(object):

	def __init__(self, conn):
		self.conn = conn

	def GetIndex():
		self.conn.send('GET /session/index.plist HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')

class ControlReplayer(object):

	def __init__(self, conn):
		self.conn = conn


	def getheader(self, len = 5):
		for i in range(1, len):
			self.conn.recvline()

	def getdata(self):
		len=''
		c = self.conn.recv(1)
		while c !='\r' and c != '\n':
			len+=c
			c = self.conn.recv(1)

		print(self.conn.recv(int('0x'+len, 16)))


	def open_stream(self):
		while True:
			c = self.conn.recv(1)
			if c != '\0':
				sys.stdout.write(c)

	def GetSessionRecordingEnabled(self):
		self.conn.send('GET /control/sessionRecordingEnabled HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')
		self.getheader(5)
		self.conn.recv()

	def GetRecordingOptions(self):
		self.conn.send('GET /control/recordingOptions HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')
		self.getheader(7)
		self.conn.recv()

class LiveReplayer(object):

	def __init__(self, conn):
		self.conn = conn

	def open_stream(self):
		while True:
			sys.stdout.write(self.conn.recv(1))

	def GetLevel(self):
		self.conn.send('GET /live/level.dat HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')
		self.open_stream()

	def GetPowerState(self):
		self.conn.send('GET /live/power_state.dat HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')
		self.open_stream()

	def GetSleeps(self):
		self.conn.send('GET /live/sleeps.dat HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')
		self.open_stream()

	def GetBluetooth(self):
		self.conn.send('GET /live/bluetooth.dat HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')
		self.open_stream()

	def GetBrightness(self):
		self.conn.send('GET /live/brightness.dat HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')
		self.open_stream()

	def GetWifi(self):
		self.conn.send('GET /live/wifi.dat HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')
		self.open_stream()

	def GetGPS(self):
		self.conn.send('GET /live/gps.dat HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')
		self.open_stream()

	def GetActivity(self):
		self.conn.send('GET /live/activity.dat HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')
		self.open_stream()

	def GetFGAppChange(self):
		self.conn.sendall('GET /live/fgapp_change.dat HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')
		self.open_stream()

	def GetPowersrcEvents(self):
		self.conn.sendall('GET /live/powersrc_events.dat HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')
		self.open_stream()

	def GetNetworkActivity(self):
		self.conn.send('GET /live/network_activity.dat HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')
		self.open_stream()

	def GetLog(self):
		self.conn.send('GET /live/log.dtx HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')
		self.open_stream()


class DTPowerClient(object):

	def __init__(self):
		self.session = None
		self.live = None
		self.control = None

	def connect(self, ip='127.0.0.1',port=7808):
		s = remote(ip, port)
		print("Connected to "+ip+" port "+str(port))
		self.session = SessionReplayer(s)
		self.control = ControlReplayer(s)
		self.live = LiveReplayer(s)


if __name__ == "__main__":
	client = DTPowerClient()
	client.connect()
	client.control.GetRecordingOptions()
	client.control.GetSessionRecordingEnabled() # Just an example
