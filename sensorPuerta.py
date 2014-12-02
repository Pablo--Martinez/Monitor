#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
import threading
import urllib2
import alertas

#eligiendo el modo de numeracion de los GPIO
GPIO.setmode(GPIO.BCM)

#Constantes del programa
PINES = [19,13,5,26,6,22]
LED_PUERTA = 12

#Configuro el pin de la alerta visual de la puerta
GPIO.setup(LED_PUERTA,GPIO.OUT)

#Path donde se encuentra el archivo de configuracion
PATH_CONF = "/home/pi/Monitor/rpi.conf"

#Constantes del emoncms
HOST_EMONCMS = "10.8.0.1"
TIME_OUT = 5

def alertar(alerta):
	alerta['ALERTANDO'] = True
	alertas.activarAlertaSonora(alerta)

def interrupcionPuerta(dispositivo,apikey,pin,tiempo_abierto,alerta):
	empezo = False

	GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	#bucle pricnipal de ejecucion
	print("\n ...Iniciando el programa...\n\n")
	while True:
		if not empezo:
			GPIO.wait_for_edge(pin,GPIO.RISING)
			empezo = True
			time_init = time.time()
			print "Inicio: %f" % time_init
			timer = threading.Timer(tiempo_abierto,alertar,args=(alerta,))
			timer.start()
			GPIO.output(LED_PUERTA,1)
			url = "http://%s/bioguard/input/post.json?json={%s:%i}&apikey=%s" % (HOST_EMONCMS,dispositivo+"_Contacto"+str(PINES.index(pin)+1),1,apikey)
                        urllib2.urlopen(url,timeout=TIME_OUT)
		
		else:
			GPIO.wait_for_edge(pin, GPIO.FALLING)
			empezo = False
			time_end = time.time() - time_init
			print "Tiempo abierto: %f \n" % time_end
			timer.cancel()
			GPIO.output(LED_PUERTA,0)
			url = "http://%s/bioguard/input/post.json?json={%s:%i}&apikey=%s" % (HOST_EMONCMS,dispositivo+"_Contacto"+str(PINES.index(pin)+1),0,apikey)
			urllib2.urlopen(url,timeout=TIME_OUT)

def sensorPuerta(dispositivo,apikey,digitales,tiempo_apertura,alerta):
	#Configuro el pin de la alerta visual de la puerta y lo seteo apagado
	GPIO.setup(LED_PUERTA,GPIO.OUT)
	GPIO.output(LED_PUERTA,0)

	for i in range(6):
		if(digitales[i] != "NULL"):
			if(digitales[i] == "Contacto"):
				t = threading.Thread(target=interrupcionPuerta,args=(dispositivo,apikey,PINES[i],tiempo_apertura,alerta))
				t.start()
			else:
				#TODO
				pass

