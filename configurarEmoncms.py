#!/usr/bin/env python

import os
import glob
import sys
import subprocess
import os
import urllib2
import json
from conf import *

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

def configurarEmoncms(dispositivo,apikey,digitales):
	
	# Esta seccion se encarga de configurar los sensores de temperatura
	for i in range(len(glob.glob(base_dir + "28*"))):
		#Obtengo el id del sensor para crear los inputs correspondientes
		feed_name = glob.glob(base_dir + "28*")[i][20:].replace("-","")

		#Chequeo que el imput que trato de crear no existe			
		url = "http://%s/bioguard/feed/getid.json?name=%s&apikey=%s" % (HOST_EMONCMS,feed_name,apikey)
		ok = json.load(urllib2.urlopen(url,timeout=TIME_OUT))
		
		#Si el feed no existe es creado
		if (ok == False): 
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

		#Si el feed existe solo se modifica su tag-name
		else:
			#Modifico el tag para el feed del sensor
			feed_id = int(ok)
			url = "http://%s/bioguard/feed/set.json?id=%i&fields={\"tag\":\"%s\"}&apikey=%s" % (HOST_EMONCMS,feed_id,dispositivo,apikey)
			urllib2.urlopen(url,timeout=TIME_OUT)

			#Modifico el tag para la alerta de temperatura alta
			url = "http://%s/bioguard/feed/getid.json?name=%s&apikey=%s" % (HOST_EMONCMS,feed_name+"_TempAlta",apikey)
                	feed_id = int(json.load(urllib2.urlopen(url,timeout=TIME_OUT)))
			url = "http://%s/bioguard/feed/set.json?id=%i&fields={\"tag\":\"%s\"}&apikey=%s" % (HOST_EMONCMS,feed_id,dispositivo,apikey)
                        urllib2.urlopen(url,timeout=TIME_OUT)
			
			#Modifico el tag para la alerta de temperatura baja
			url = "http://%s/bioguard/feed/getid.json?name=%s&apikey=%s" % (HOST_EMONCMS,feed_name+"_TempBaja",apikey)
                	feed_id = int(json.load(urllib2.urlopen(url,timeout=TIME_OUT)))
			url = "http://%s/bioguard/feed/set.json?id=%i&fields={\"tag\":\"%s\"}&apikey=%s" % (HOST_EMONCMS,feed_id,dispositivo,apikey)
                        urllib2.urlopen(url,timeout=TIME_OUT)



	# Esta seccion se encarga de configurar los pines digitales
	for i in range(6):
		if(digitales[i] != "NULL"):
			if(digitales[i] == "Contacto"):
				feed_name = nombre + "_Contacto" + str(i+1)
			else:
				feed_name = nombre + "_Alterna" + str(i+1)
		
			#Chequeo que el imput que trato de crear no existe
                	url = "http://%s/bioguard/feed/getid.json?name=%s&apikey=%s" % (HOST_EMONCMS,feed_name,apikey)
                	ok = json.load(urllib2.urlopen(url,timeout=TIME_OUT))

			if (ok == False):
	                        #Creo los inputs para el sensor digital
        	                url = "http://%s/bioguard/input/post.json?json={%s:0}&apikey=%s" % (HOST_EMONCMS,feed_name,apikey)
                	        urllib2.urlopen(url,timeout=TIME_OUT)

				#Creo el feed que esta asociado al input anterior
				url = "http://%s/bioguard/feed/create.json?name=%s&datatype=1&engine=6&options={\"interval\":\"10\"}&apikey=%s" % (HOST_EMONCMS,feed_name,apikey)
				result = json.load(urllib2.urlopen(url,timeout=TIME_OUT))
		
				if(result["success"]):
					feed_id = result["feedid"]
					url = "http://%s/bioguard/feed/set.json?id=%i&fields={\"tag\":\"%s\"}&apikey=%s" % (HOST_EMONCMS,feed_id,dispositivo,apikey)
					urllib2.urlopen(url,timeout=TIME_OUT)
				
					#Creo el proceso asociado al sensor digital y al feed anterior
					url = "http://%s/bioguard/input/list.json&apikey=%s" % (HOST_EMONCMS,apikey)
					inputs = json.load(urllib2.urlopen(url,timeout=TIME_OUT))
					for i in range(len(inputs)):
						if(inputs[i]["name"] == feed_name):
							input_id = int(inputs[i]["id"])
							url = "http://%s/bioguard/input/process/add.json?inputid=%i&processid=1&arg=%i&newfeedname=%s&options={\"interval\":\"10\",\"engine\":\"6\"}&apikey=%s" % (HOST_EMONCMS,input_id,feed_id,feed_name,apikey)
							urllib2.urlopen(url,timeout=TIME_OUT)
							break
		
			#Si el feed existe solo se modifica su tag-name
			else:
				#Modifico el tag para el feed del pin digital
				feed_id = int(ok)
				url = "http://%s/bioguard/feed/set.json?id=%i&fields={\"tag\":\"%s\"}&apikey=%s" % (HOST_EMONCMS,feed_id,dispositivo,apikey)
				urllib2.urlopen(url,timeout=TIME_OUT)


if __name__ == "__main__":
	
	try:
		conf = open(PATH_CONF,"r")
		text_conf = conf.readlines()
		conf.close()
		nombre = text_conf[0].split(" ")[1][:-1]
		apikey = text_conf[2].split(" ")[1][:-1]
		digitales = text_conf[5].split(" ")[1:-1]
		configurarEmoncms(nombre,apikey,digitales)
	
	except:
		exit
