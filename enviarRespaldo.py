#!/usr/bin/env python

import urllib2
import os

HOST_EMONCMS = "ec2-54-213-91-62.us-west-2.compute.amazonaws.com"
APIKEY = "c25ceb2b2537468859d5afc4e5aa9095" # apikey del cliente (usuario de emoncms)
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
		url = "http://%s/emoncms/input/post.json?time=%s&csv={%s}&apikey=%s" % (HOST_EMONCMS,timestamp,datos,APIKEY)
		
		try:
			urllib2.urlopen(url,timeout=TIME_OUT)
			
		except urllib2.URLError, e:
			print e.reason
					
	# Cierro el fichero y lo elimino para no enviar los mismos datos la siguiente vez
	log.close()
	os.remove(PATH_LOG)
		
except:
	pass
