#!/usr/bin/python
"""
This module contains a simple HTTP interface to control hyperion-audio-effects
and the effects that come with hyperion. It also provides a button to shut down
the system.

Created on 08/09/2016

@author: Alexander Fell
"""


from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import json
import argparse
import subprocess
import threading
import commentjson
from urlparse import parse_qs


class Shutdown(object):
	def __init__(self):
		self.shutdown = False

	def execute(self):
		musicControl.kill()
		process = subprocess.Popen(['hyperion-remote', '--clearall'], stdout=subprocess.PIPE)
		process.wait()
		process = subprocess.Popen(['sudo', 'shutdown'])
		self.shutdown = True

	def cancel(self):
		if self.shutdown:
			process = subprocess.Popen(['sudo', 'shutdown', '-c'])
			self.shutdown = False

			


class MusicControl(object):
	def __init__(self):
		self.musicChild = None


	def startEffect(self, effect):
		self.musicChild = subprocess.Popen([os.path.dirname(os.path.abspath(__file__))+'/main.py', '--effect', effect], stdin=subprocess.PIPE)
		print 'Spawning hyperion-audio-effect --effect '+effect


	def kill(self):
		if self.musicChild is None:
			print "Music Child does not exist."
			return

		self.musicChild.communicate(input='x\n')
		self.musicChild.wait()
		self.musicChild = None
		print "Music Child terminated."



class LightControl(object):
	def __init__(self):
		self.active = True
		self.stopThread = False
		self.interval = 3
		self.countDown = self.interval
		self.checkLEDStatus()

	def checkLEDStatus(self):
		if self.stopThread:
			return

		threading.Timer(1, self.checkLEDStatus).start()
		if self.active:
			self.countDown -= 1
			if self.countDown == 0:
				self.countDown = self.interval
				process = subprocess.Popen(['hyperion-remote', '-c', 'ffd385'])
		else:
			self.countDown = self.interval


	def stop(self):
		self.stopThread = True
		



#-- The class is reinstantiated every time, a request is received
class HTTPRequest(BaseHTTPRequestHandler):

	def __init__(self, request, client_address, server):
		self.menu = {'Main Menu': '/', 'Video Effects': 'getEffectList.html', 'Music Effects': 'musicEffects.html'}
		BaseHTTPRequestHandler.__init__(self, request, client_address, server)

	#Handler for the GET requests
	def do_GET(self):

		# Send the html message
		if self.path == '/':
			self.getIndexFile()
		elif self.path.startswith('/style.css'):
			self.getCSSstyle()
		elif self.path.startswith('/getEffectList.html'):
			self.getEffectList()
		elif self.path.startswith('/musicEffects.html'):
			self.musicEffects()
		elif self.path.startswith('/shutdown.html'):
			self.shutDown()
		elif self.path.startswith('/favicon.ico'):
			self.favicon()
		else:
			print self.path+" not found."
			self.send_error(404, "File ("+self.path+") not found")


	def getIndexFile(self):
		self.sendHeader()
		self.wfile.write("<h1>Main Menu</h1>")
		self.wfile.write("<nav><ul>")

		
		keys = self.menu.keys()
		for i in keys:
			self.wfile.write("<li><form action=\""+self.menu[i]+"\"><input type=\"submit\" value=\""+i+"\"></form></li>")

		self.wfile.write("<li><form action=\"shutdown.html\"><input type=\"submit\" value=\"Shutdown\"></form></li>")
		self.wfile.write("</nav></ul>")
		self.sendFooter();


	def getCSSstyle(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/css')
		self.end_headers()
		self.getFile('style.css')
		self.sendFooter();



	def musicEffects(self):
		effects = []
		for effect in os.listdir(os.path.dirname(os.path.abspath(__file__))+"/effects"):
			if effect.endswith(".json"):
				effects.append(effect[:-5])

		self.sendHeader()
		self.printMenu()
		self.wfile.write("<h1>Music Effects</h1>")
		self.wfile.write("<nav><ul>")
		for effect in effects:
			self.wfile.write("<li><form action=\"musicEffects.html\"><input type=\"submit\" name=\"effect\" value=\""+effect+"\"></form></li>")

		self.wfile.write("<li><form action=\"musicEffects.html\"><input type=\"submit\" name=\"effect\" value=\"Clear\"></form></li>")
		self.wfile.write("</nav></ul>")


		selection = parse_qs(self.path[19:])
		if selection:
			musicControl.kill()

			if selection['effect'][0] == 'Clear':
				process = subprocess.Popen(['hyperion-remote', '--clearall'], stdout=subprocess.PIPE)
			else:
				self.wfile.write("<h3>Selected effect: "+selection['effect'][0]+"</h3>")
				musicControl.startEffect(selection['effect'][0])


		self.sendFooter();




	def getEffectList(self):
		self.sendHeader()
		self.printMenu()
		if not self.checkHyperionActive():
			return

		process = subprocess.Popen(['hyperion-remote', '--list'], stdout=subprocess.PIPE)

		lines = ''
		start = False
		for line in process.stdout: 
			if line.startswith('{'):
				start=True
			if start:
				lines += line

		jsonObj = json.loads(lines)

		#print(lines)

		self.wfile.write("<h1>Effects</h1>")
		self.wfile.write("<nav><ul>")
		for effect in jsonObj['effects']:
			self.wfile.write("<li><form action=\"getEffectList.html\"><input type=\"submit\" name=\"effect\" value=\""+effect['name']+"\"></form></li>")

		self.wfile.write("<li><form action=\"getEffectList.html\"><input type=\"submit\" name=\"effect\" value=\"Clear\"></form></li>")
		self.wfile.write("</nav></ul>")

		selection = parse_qs(self.path[20:])
		if selection:
			musicControl.kill()

			if selection['effect'][0] == 'Clear':
				process = subprocess.Popen(['hyperion-remote', '--clearall'], stdout=subprocess.PIPE)
			else:
				self.wfile.write("<h3>Selected effect: "+selection['effect'][0]+"</h3>")
				process = subprocess.Popen(['hyperion-remote', '-e', selection['effect'][0]], stdout=subprocess.PIPE)
#			for line in process.stdout: 
#				print line

		

		self.sendFooter();
		

	def shutDown(self):
		self.sendHeader()
		self.printMenu()
		self.wfile.write("<h1>Shutting down...</h1>")
		self.wfile.write("<h3>Shut down executed in 60 seconds. Click on any menu item to cancel the shutdown countdown.</h3>")

		self.sendFooter()
		shutdown.execute()


	def favicon(self):
		self.send_response(200)
		self.send_header('Content-type', 'image/x-icon')
		self.end_headers()
		self.getFile("favicon.ico")


	def printMenu(self):
		shutdown.cancel()
		keys = self.menu.keys()
		for i in keys:
			self.wfile.write(" | <a href=\""+self.menu[i]+"\">"+i+"</a>")



	def getFile(self, filename):
		f = open(os.path.dirname(os.path.abspath(__file__))+'/'+filename, "rb")
		self.wfile.write(f.read())
		f.close()


	def sendHeader(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		self.wfile.write("<html><head>")
		self.wfile.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">")
		self.wfile.write("<title>Hyperion HTTP Remote Control</title>")
		self.wfile.write("<link rel=\"icon\" href=\"/favicon.ico\" type=\"image/x-icon\">")
		self.wfile.write("</head><body>")


	def sendFooter(self):
		self.wfile.write("</body></html>")


	
	def checkHyperionActive(self):
		process = subprocess.Popen(['hyperion-remote', '-l'], stdout=subprocess.PIPE)
		process.communicate()

		if process.returncode != 0:
			print 'Hyperion is not active!'
			self.wfile.write("<br><font color=\"red\"><strong>Hyperion inactive!</strong></font>")
			return False
		else:
			self.wfile.write("<br><font color=\"green\">Hyperion inactive!</font>")
			return True




def create_parser(config):
	parser = argparse.ArgumentParser()
	parser.add_argument("--port",
			help="port number of the webserver",
			default=config['webserver']['port'],
			type=int)
	return parser

def read_config(file_path):
	with open(file_path) as config_json:
		return commentjson.load(config_json)



def run():
	directory = os.path.dirname(os.path.realpath(__file__))
	args = create_parser(read_config(directory+'/config.json')).parse_args()

	try:
		print 'HTTP Server is starting...'
		server = HTTPServer(('', args.port), HTTPRequest)
		print 'Started http server on port' , args.port

		#Wait forever for incoming htto requests
		server.serve_forever()

	except KeyboardInterrupt:
		print '^C received, shutting down the web server'
		musicControl.kill()
#		lightControl.stop()	
		process = subprocess.Popen(['hyperion-remote', '--clearall'], stdout=subprocess.PIPE)
		process.wait()
		server.socket.close


if __name__ == '__main__':
	musicControl = MusicControl()
#	lightControl = LightControl()
	shutdown = Shutdown()
	run()
