#!/usr/bin/env python

import urllib2
import os

HOST_EMONCMS = "10.8.0.1"
APIKEY = "" # APIKEY del usuario de emoncms
PATH_LOG = "/home/pi/Monitor/perdidos.log"

TIME_OUT = 5

try:
	log = open(PATH_LOG,"r")
	lineas = log.readlines()
	for linea in lineas:
		linea = linea[:-1]
		
		# Obtengo la fecha
		timestamp = linea.split(" ")[0]
		
		# Obtengo los datos de temperatura 
		datos = linea.split(" ")[1]
		
		# Construyo la url a partir de los datos
		url = "http://%s/bioguard/input/post.json?time=%s&csv={%s}&apikey=%s" % (HOST_EMONCMS,timestamp,datos,APIKEY)
		
		try:
			urllib2.urlopen(url,timeout=TIME_OUT)
			
		except urllib2.URLError, e:
			print e.reason
					
	# Cierro el fichero y lo elimino para no enviar los mismos datos la siguiente vez
	log.close()
	os.remove(PATH_LOG)
		
except:
	pass
