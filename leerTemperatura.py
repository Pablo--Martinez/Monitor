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

HOST_EMONCMS = "10.8.0.1"
PATH_CONF = "/home/pi/Monitor/rpi.conf"
PATH_LOG = "/home/pi/Monitor/perdidos.log"

TIME_OUT = 5
PIN_ALTA = 14
PIN_BAJA = 18

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_ALTA,GPIO.OUT)
GPIO.setup(PIN_BAJA,GPIO.OUT)
GPIO.output(PIN_ALTA,0)
GPIO.output(PIN_BAJA,0)

base_dir = '/sys/bus/w1/devices/'

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

def leerTemperatura(ciclo,apikey,minimo,maximo):
	while True:
		#Obtengo la fecha para almacenar
		date = timegm(datetime.now().utctimetuple())				

		#Para generar la estructura del json
		datos = ""
		temp_alta = False
		temp_baja = False

		for i in range(len(glob.glob(base_dir + "28*"))):
			path = glob.glob(base_dir + "28*")[i] + "/w1_slave"

			#Leo la temperatura para ese sensor
			temp = read_temp(path)

			#Enciendo los LEDS correspondientes en caso de estar fuera de temperatura
			if((not temp_alta) and (temp > maximo)):
				temp_alta = True							

			if((not temp_baja) and (temp < minimo)):
				temp_baja = True
			
			#Obtengo el nombre de ese feed para esa temperatura
			feed_name = path[20:35].replace("-","")
			datos += "%s:%f," % (feed_name,temp)
	
		#Si la temperatura esta por encima del maximo prendo el LED
		if(temp_alta):
			GPIO.output(PIN_ALTA,1)
		#Caso contrario lo apago
		else:
			GPIO.output(PIN_ALTA,0)

		#Si la temperatura esta por debajo del maximo prendo el LED
		if(temp_baja):
			GPIO.output(PIN_BAJA,1)
		#Caso contrario lo apago
		else:
			GPIO.output(PIN_BAJA,0)
		
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
	
if __name__ == "__main__":	
	
	try:
		conf = open(PATH_CONF,"r")
		text_conf = conf.readlines()
		conf.close()
		ciclo = int(text_conf[1].split(" ")[1][:-1])
		apikey = text_conf[2].split(" ")[1][:-1]
		minimo = float(text_conf[3].split(" ")[1][:-1])
		maximo = float(text_conf[4].split(" ")[1][:-1])

		leerTemperatura(ciclo,apikey,minimo,maximo)
		
	except:
		exit
