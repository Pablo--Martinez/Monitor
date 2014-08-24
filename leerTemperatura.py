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

HOST_EMONCMS = "ec2-54-213-91-62.us-west-2.compute.amazonaws.com"
APIKEY = "c25ceb2b2537468859d5afc4e5aa9095"

TIME_OUT = 5

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

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


if __name__ == "__main__":	
	while True:
		#Obtengo la fecha para almacenar
		#date = timegm(datetime.now().utctimetuple())	
		date = datetime.now().strftime('%Y-%m-%d %H:%M')				

		#Para generar la estructura del json
		datos = ""

		for i in range(len(glob.glob(base_dir + "28*"))):
			path = glob.glob(base_dir + "28*")[i] + "/w1_slave"

			#Leo la temperatura para ese sensor
			temp = read_temp(path)
			
			#Obtengo el nombre de ese feed para esa temperatura
			feed_name = path[20:35].replace("-","")
			datos += "%s:%f," % (feed_name,temp)

		try:
			#Inserto el dato de temperatura para ese feed_name
			url = "http://%s/emoncms/input/post.json?json={%s}&apikey=%s" % (HOST_EMONCMS,datos[:-1],APIKEY)
	                urllib2.urlopen(url,timeout=TIME_OUT)
			
		except:	
			log = open("perdidos.log","a")
			linea = date + " " + datos[:-1] + "\n"
			log.write(linea)
			log.close() 
			
		sleep(60)
	

