#!/usr/bin/env python

import urllib2
import os

HOST_EMONCMS = "10.8.0.1"
APIKEY = "c25ceb2b2537468859d5afc4e5aa9095" # apikey del cliente (usuario de emoncms)
PATH_LOG = "/home/pi/Monitor/perdidos.log"

TIME_OUT = 5

def enviarRespaldo(apikey)
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
			url = "http://%s/bioguard/input/post.json?time=%s&csv={%s}&apikey=%s" % (HOST_EMONCMS,timestamp,datos,apikey)
			
			try:
				urllib2.urlopen(url,timeout=TIME_OUT)
				
			except urllib2.URLError, e:
				print e.reason
					
		# Cierro el fichero y lo elimino para no enviar los mismos datos la siguiente vez
		log.close()
		os.remove(PATH_LOG)
		
	except:
		exit



if __name__ == "__main__":
	
	try:
		conf = open(PATH_CONF,"r")
		text_conf = conf.readlines()
		conf.close()
		apikey = text_conf[2].split(" ")[1][:-1]
		enviarRespaldo(apikey)
		
	except:
		exit

