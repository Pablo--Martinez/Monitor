#!/usr/bin/env python

import os
import glob
import sys
from datetime import datetime
from calendar import timegm
import subprocess
import os
from time import sleep
import urllib2
import json
import RPi.GPIO as GPIO
import alertas
from conf import *

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_ALTA,GPIO.OUT)
GPIO.setup(PIN_BAJA,GPIO.OUT)
GPIO.output(PIN_ALTA,0)
GPIO.output(PIN_BAJA,0)

base_dir = '/sys/bus/w1/devices/'

def alertar(alerta,temp=0,rom=0):
        alerta['ALERTANDO'] = True
        alertas.activarAlertaSonora(alerta)
	alertas.enviarAlertas(alerta,"TEMP_ALTA",temp=temp,rom=rom)

def read_temp_raw(path):
	f = open(path,'r')
	lines = f.readlines()
        f.close()
        return lines

def read_temp(path):
        lines = read_temp_raw(path)
        while lines[0].strip()[-3:] != 'YES':
        	time.sleep(0.2)
                lines = read_temp_raw(path)
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
  	        return temp_c

def leerTemperatura(ciclo,apikey,minimo,maximo,ALERTAS):
	temp_alta = [False,False,False,False]
	temp_baja = [False,False,False,False]
	
	#Obtengo como esta el estado actual de las alamras
	for i in range(len(glob.glob(base_dir + "28*"))):
	        path = glob.glob(base_dir + "28*")[i] + "/w1_slave"
		feed_name = path[20:35].replace("-","")
		
		#Actualizo la temp alta
		url = "http://%s/bioguard/feed/getid.json?name=%s&apikey=%s" % (HOST_EMONCMS,feed_name+"_TempAlta",apikey)
                id = int(json.load(urllib2.urlopen(url,timeout=TIME_OUT)))
		
		url = "http://%s/bioguard/feed/value.json?id=%i&apikey=%s" % (HOST_EMONCMS,id,apikey)
		alerta = int(json.load(urllib2.urlopen(url,timeout=TIME_OUT)))
		if(alerta == 1):
			temp_alta[i] = True

		#Actualizo la temp baja
		url = "http://%s/bioguard/feed/getid.json?name=%s&apikey=%s" % (HOST_EMONCMS,feed_name+"_TempBaja",apikey)
                id = int(json.load(urllib2.urlopen(url,timeout=TIME_OUT)))

                url = "http://%s/bioguard/feed/value.json?id=%i&apikey=%s" % (HOST_EMONCMS,id,apikey)
                alerta = int(json.load(urllib2.urlopen(url,timeout=TIME_OUT)))
                if(alerta == 1):
                        temp_baja[i] = True
		
	#While principal para obtener datos de manera periodica
	while True:
		#Obtengo la fecha para almacenar
		date = timegm(datetime.now().utctimetuple())				

		#Para generar la estructura del json
		datos = ""

		for i in range(len(glob.glob(base_dir + "28*"))):
			path = glob.glob(base_dir + "28*")[i] + "/w1_slave"

			#Leo la temperatura para ese sensor
			temp = read_temp(path)

			#Obtengo el nombre de ese feed para esa temperatura
                        feed_name = path[20:35].replace("-","")
                        datos += "%s:%f," % (feed_name,temp)

			#Enciendo los LEDS correspondientes en caso de estar fuera de temperatura
			if(temp > maximo):
				ALERTAS['FUERA_TEMP'] = True
				#alertar(ALERTAS) => ESTABA ACA
				if((not temp_alta[i])): #Para no enviar de nuevo al servidor
					alertar(ALERTAS,temp,feed_name)
					temp_alta[i] = True							
					GPIO.output(PIN_ALTA,1)
					datos += "%s:%i," % (feed_name+"_TempAlta",1)

			elif((temp_alta[i]) and (temp < maximo)):
				ALERTAS['FUERA_TEMP'] = False
				temp_alta[i] = False
				GPIO.output(PIN_ALTA,0)
				datos += "%s:%i," % (feed_name+"_TempAlta",0)

			if(temp < minimo):
				ALERTAS['FUERA_TEMP'] = True
				#alertar(ALERTAS) => ESTABA ACA
				if((not temp_baja[i])): #Para no enviar de nuevo al servidor
					alertar(ALERTAS,temp,feed_name)
					temp_baja[i] = True
					GPIO.output(PIN_BAJA,1)
					datos += "%s:%i," % (feed_name+"_TempBaja",1)

			elif((temp_baja[i]) and (temp > minimo)):
				ALERTAS['FUERA_TEMP'] = False
                                temp_baja[i] = False 
				GPIO.output(PIN_BAJA,0)
				datos += "%s:%i" % (feed_name+"_TempBaja",0)
			
		try:
			#Inserto el dato de temperatura para ese feed_name
			url = "http://%s/bioguard/input/post.json?json={%s}&apikey=%s" % (HOST_EMONCMS,datos[:-1],apikey)
			urllib2.urlopen(url,timeout=TIME_OUT)
			
		except:	
			log = open(PATH_LOG,"a")
			linea = str(date) + " " + datos[:-1] + "\n"
			log.write(linea)
			log.close() 
			
		sleep(60 * int(ciclo))
