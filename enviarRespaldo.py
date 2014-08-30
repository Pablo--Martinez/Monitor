#!/usr/bin/env python

import urllib2
import os

HOST_EMONCMS = "10.8.0.1"
PATH_LOG = "/home/pi/Monitor/perdidos.log"
PATH_CONF = "/home/pi/Monitor/rpi.conf"

TIME_OUT = 5

def enviarRespaldo(apikey):
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
				# Cierro el fichero y lo elimino para no enviar los mismos datos la siguiente vez
				log.close()
				os.remove(PATH_LOG)
				
			except urllib2.URLError, e:
				print e.reason
				log.close()		
		
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

