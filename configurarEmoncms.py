#!/usr/bin/env python

import os
import glob
import sys
import subprocess
import os
import urllib2
import json


HOST_EMONCMS = "ec2-54-213-91-62.us-west-2.compute.amazonaws.com"
APIKEY = "c25ceb2b2537468859d5afc4e5aa9095"

TIME_OUT = 5

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

def configurarEmoncms(dispositivo):
	for i in range(len(glob.glob(base_dir + "28*"))):
		#Obtengo el id del sensor para crear los inputs correspondientes
		feed_name = glob.glob(base_dir + "28*")[i][20:].replace("-","")
			
		#Creo los inputs para los sensores conectados
		url = "http://%s/emoncms/input/post.json?json={%s:0}&apikey=%s" % (HOST_EMONCMS,feed_name,APIKEY)
		urllib2.urlopen(url,timeout=TIME_OUT)

		#Creo los feeds para las alertas de los sensores conectados
		url = "http://%s/emoncms/feed/create.json?name=%s&apikey=%s" % (HOST_EMONCMS,feed_name + "_TempAlta",APIKEY)
		feed_id = json.load(urllib2.urlopen(url,timeout=TIME_OUT))['feedid']
		url = "http://%s/emoncms/feed/set.json?id=%i&fields={\"tag\":\"%s\"}&apikey=%s" % (HOST_EMONCMS,feed_id,dispositivo,APIKEY)
		urllib2.urlopen(url,timeout=TIME_OUT)

		url = "http://%s/emoncms/feed/create.json?name=%s&apikey=%s" % (HOST_EMONCMS,feed_name + "_TempBaja",APIKEY)
		#urllib2.urlopen(url,timeout=TIME_OUT)
		feed_id = json.load(urllib2.urlopen(url,timeout=TIME_OUT))["feedid"]
                url = "http://%s/emoncms/feed/set.json?id=%i&fields={\"tag\":\"%s\"}&apikey=%s" % (HOST_EMONCMS,feed_id,dispositivo,APIKEY)
                urllib2.urlopen(url,timeout=TIME_OUT)
	
		#Creo los feeds para que sean los procesos de los inputs
		url = "http://%s/emoncms/feed/create.json?name=%s&datatype=1&engine=6&options={\"interval\":\"10\"}&apikey=%s" % (HOST_EMONCMS,feed_name,APIKEY)
		feed_id = json.load(urllib2.urlopen(url,timeout=TIME_OUT))["feedid"]
		url = "http://%s/emoncms/feed/set.json?id=%i&fields={\"tag\":\"%s\"}&apikey=%s" % (HOST_EMONCMS,feed_id,dispositivo,APIKEY)
                urllib2.urlopen(url,timeout=TIME_OUT)
	
		#Creo los procesos para esos inputs, necesito el input_id
		url = "http://%s/emoncms/input/list.json&apikey=%s" % (HOST_EMONCMS,APIKEY)
		inputs = json.load(urllib2.urlopen(url,timeout=TIME_OUT))
		for i in range(len(inputs)):
			if(inputs[i]["name"] == feed_name):
				input_id = int(inputs[i]["id"])
				break
			
		url = "http://%s/emoncms/input/process/add.json?inputid=%i&processid=1&arg=%i&newfeedname=%s&options={\"interval\":\"10\",\"engine\":\"6\"}&apikey=%s" % (HOST_EMONCMS,input_id,feed_id,feed_name,APIKEY)
		urllib2.urlopen(url,timeout=TIME_OUT)



if __name__ == "__main__":
	if(len(sys.argv) == 2):
		configurarEmoncms(str(sys.argv[1]))
		print "Configuracion realizada con exito!"
	
	else:
		print "Para configurar ejecute sudo ./configurarEmoncms.py dispositivo"

