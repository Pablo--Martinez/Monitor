#!/usr/bin/env python

import os
import glob
import sys
import subprocess
import os
import urllib2
import json


HOST_EMONCMS = "10.8.0.1"
PATH_CONF = "/home/pi/Monitor/rpi.conf"

TIME_OUT = 5

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

def configurarEmoncms(dispositivo,apikey):
	for i in range(len(glob.glob(base_dir + "28*"))):
		#Obtengo el id del sensor para crear los inputs correspondientes
		feed_name = glob.glob(base_dir + "28*")[i][20:].replace("-","")
			
		#Creo los inputs para los sensores conectados
		url = "http://%s/bioguard/input/post.json?json={%s:0}&apikey=%s" % (HOST_EMONCMS,feed_name,apikey)
		urllib2.urlopen(url,timeout=TIME_OUT)
		
		#Creo los input para las advertencias de los sensores conectados
		#Temperatura alta
		url = "http://%s/bioguard/input/post.json?json={%s:0}&apikey=%s" % (HOST_EMONCMS,feed_name + "_TempAlta",apikey)
		urllib2.urlopen(url,timeout=TIME_OUT)
				
		#Temperatura baja
		url = "http://%s/bioguard/input/post.json?json={%s:0}&apikey=%s" % (HOST_EMONCMS,feed_name + "_TempBaja",apikey)
		urllib2.urlopen(url,timeout=TIME_OUT)
				
		#Creo los feeds para que sean los procesos de los inputs
		#Feed de datos
		try:
			url = "http://%s/bioguard/feed/create.json?name=%s&datatype=1&engine=6&options={\"interval\":\"10\"}&apikey=%s" % (HOST_EMONCMS,feed_name,apikey)
			result = json.load(urllib2.urlopen(url,timeout=TIME_OUT))
		
			if(result["success"]):
				feed_id = result["feedid"]
				url = "http://%s/bioguard/feed/set.json?id=%i&fields={\"tag\":\"%s\"}&apikey=%s" % (HOST_EMONCMS,feed_id,dispositivo,apikey)
				urllib2.urlopen(url,timeout=TIME_OUT)
			
				#Creo los procesos para esos inputs, necesito el input_id
				url = "http://%s/bioguard/input/list.json&apikey=%s" % (HOST_EMONCMS,apikey)
				inputs = json.load(urllib2.urlopen(url,timeout=TIME_OUT))
				for i in range(len(inputs)):
					if(inputs[i]["name"] == feed_name):
						input_id = int(inputs[i]["id"])
						url = "http://%s/bioguard/input/process/add.json?inputid=%i&processid=1&arg=%i&newfeedname=%s&options={\"interval\":\"10\",\"engine\":\"6\"}&apikey=%s" % (HOST_EMONCMS,input_id,feed_id,feed_name,apikey)
						urllib2.urlopen(url,timeout=TIME_OUT)
						break

		except:
			print "ADVERTENCIA: Feed %s ya existe" % feed_name
		
		#Feed para temperatura alta
		try:
			url = "http://%s/bioguard/feed/create.json?name=%s&datatype=1&engine=6&options={\"interval\":\"10\"}&apikey=%s" % (HOST_EMONCMS,feed_name+"_TempAlta",apikey)
                        result = json.load(urllib2.urlopen(url,timeout=TIME_OUT))

	                if(result["success"]):
	                        feed_id = result["feedid"]
	                        url = "http://%s/bioguard/feed/set.json?id=%i&fields={\"tag\":\"%s\"}&apikey=%s" % (HOST_EMONCMS,feed_id,dispositivo,apikey)
	                        urllib2.urlopen(url,timeout=TIME_OUT)

        	                #Creo los procesos para esos inputs, necesito el input_id
	                        url = "http://%s/bioguard/input/list.json&apikey=%s" % (HOST_EMONCMS,apikey)
	                        inputs = json.load(urllib2.urlopen(url,timeout=TIME_OUT))
				
			for i in range(len(inputs)):
				if(inputs[i]["name"] == feed_name + "_TempAlta"):
					input_id = int(inputs[i]["id"])
					url = "http://%s/bioguard/input/process/add.json?inputid=%i&processid=1&arg=%i&newfeedname=%s&options={\"interval\":\"10\",\"engine\":\"6\"}&apikey=%s" % (HOST_EMONCMS,input_id,feed_id,feed_name+"_TempAlta",apikey)
					urllib2.urlopen(url,timeout=TIME_OUT)
					break
		except:
                        print "ADVERTENCIA: Feed %s ya existe" % feed_name+"_TempAlta"
					
		#Feed para temperatura baja
		try:
			url = "http://%s/bioguard/feed/create.json?name=%s&datatype=1&engine=6&options={\"interval\":\"10\"}&apikey=%s" % (HOST_EMONCMS,feed_name+"_TempBaja",apikey)
                        result = json.load(urllib2.urlopen(url,timeout=TIME_OUT))

	                if(result["success"]):
	                        feed_id = result["feedid"]
	                        url = "http://%s/bioguard/feed/set.json?id=%i&fields={\"tag\":\"%s\"}&apikey=%s" % (HOST_EMONCMS,feed_id,dispositivo,apikey)
	                        urllib2.urlopen(url,timeout=TIME_OUT)

	                        #Creo los procesos para esos inputs, necesito el input_id
	                        url = "http://%s/bioguard/input/list.json&apikey=%s" % (HOST_EMONCMS,apikey)
	                        inputs = json.load(urllib2.urlopen(url,timeout=TIME_OUT))
	                        for i in range(len(inputs)):
	                                if(inputs[i]["name"] == feed_name + "_TempBaja"):
	                                        input_id = int(inputs[i]["id"])
						url = "http://%s/bioguard/input/process/add.json?inputid=%i&processid=1&arg=%i&newfeedname=%s&options={\"interval\":\"10\",\"engine\":\"6\"}&apikey=%s" % (HOST_EMONCMS,input_id,feed_id,feed_name+"_TempBaja",apikey)
	                                        urllib2.urlopen(url,timeout=TIME_OUT)
	                                        break

		except:
                        print "ADVERTENCIA: Feed %s ya existe" % feed_name+"_TempBaja"


if __name__ == "__main__":
	
	try:
		conf = open(PATH_CONF,"r")
		text_conf = conf.readlines()
		conf.close()
		nombre = text_conf[0].split(" ")[1][:-1]
		apikey = text_conf[2].split(" ")[1][:-1]
		configurarEmoncms(nombre,apikey)
				
	except:
		exit
