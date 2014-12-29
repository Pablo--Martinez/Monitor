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

#Path donde se guardan los respaldos de las alertas que no son enviadas
PATH_LOG_ALERTAS = "/home/pi/Monitor/alertas.log"

#Constantes del emoncms
HOST_EMONCMS = "10.8.0.1"
TIME_OUT = 5

def alertar(alerta):
	alerta['ALERTANDO'] = True
	alertas.activarAlertaSonora(alerta)

def interrupcionDigital(tipo,dispositivo,apikey,pin,tiempo_abierto,alerta):
	empezo = False

	GPIO.setup(pin, GPIO.IN)

	#bucle pricnipal de ejecucion
	print "Iniciando entrada digital %s como %s\n" % (str(PINES.index(pin)+1),tipo)
	while True:
		if not empezo:
			GPIO.wait_for_edge(pin,GPIO.FALLING)
			if(GPIO.input(pin) == 0):
				alerta["ABIERTO"] = True
				empezo = True
				time_init = time.time()
				timer = threading.Timer(tiempo_abierto,alertar,args=(alerta,))
				timer.start()
				GPIO.output(LED_PUERTA,1)
				url = "http://%s/bioguard/input/post.json?json={%s:%i}&apikey=%s" % (HOST_EMONCMS,dispositivo+"_" + tipo +str(PINES.index(pin)+1),1,apikey)
				try:
					urllib2.urlopen(url,timeout=TIME_OUT)
				except:
					log = open(PATH_LOG_ALERTAS,"a")
	                        	linea = str(timegm(datetime.now().utctimetuple())) + " %s:%i\n" % (str(PINES.index(pin)+1),1)
	                        	log.write(linea)
					log.close()
		
		else:
			GPIO.wait_for_edge(pin, GPIO.RISING)
			if(GPIO.input(pin) == 1):
				alerta["ABIERTO"] = False
				empezo = False
				time_end = time.time() - time_init
				timer.cancel()
				GPIO.output(LED_PUERTA,0)
				url = "http://%s/bioguard/input/post.json?json={%s:%i}&apikey=%s" % (HOST_EMONCMS,dispositivo+"_" + tipo + str(PINES.index(pin)+1),0,apikey)
				try:
					urllib2.urlopen(url,timeout=TIME_OUT)
				except:
					log = open(PATH_LOG_ALERTAS,"a")
					linea = str(timegm(datetime.now().utctimetuple())) + " %s:%i\n" % (str(PINES.index(pin)+1),0)
					log.write(linea)
					log.close()

def sensoresDigitales(dispositivo,apikey,digitales,tiempo_apertura,alerta):
	#Configuro el pin de la alerta visual de la puerta y lo seteo apagado
	GPIO.setup(LED_PUERTA,GPIO.OUT)
	GPIO.output(LED_PUERTA,0)

	# Para cada sensor digital habilitado ejecuto un thread que se encarga de controlar dicha entrada, siendo de puerta o alterna
	for i in range(6):
		if(digitales[i] != "NULL"):
			t = threading.Thread(target=interrupcionDigital,args=(digitales[i],dispositivo,apikey,PINES[i],tiempo_apertura,alerta))
			t.start()

