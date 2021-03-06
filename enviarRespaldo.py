#!/usr/bin/env python

import urllib2
import os
from conf import *

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
		response = os.system("ping -c 5 " + HOST_EMONCMS)
		if(response == 0):
			conf = open(PATH_CONF,"r")
			text_conf = conf.readlines()
			conf.close()
			apikey = text_conf[2].split(" ")[1][:-1]
			enviarRespaldo(apikey)
		
	except:
		exit

