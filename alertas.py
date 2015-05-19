#!/usr/bin/env python

"""
Este script solamente contiene las funciones que se engargan de las alertas locales
y las que seran luego enviadas al servidor para enviar un mail/mensaje/llamada al cliente
"""
import threading
import urllib2
import json
from time import sleep
import RPi.GPIO as GPIO
from conf import *

def setupAlertas():
	"""
	Esta funcion configura el pin del buzzer y lo setea apagado
	"""
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(PIN_BUZZER,GPIO.OUT)
	GPIO.output(PIN_BUZZER,0)

def encenderBuzzer(alertas):
	"""
	Esta funcion se encarga de encender y apagar el buzzer de forma periodica, cuando
	termina la alerta el buzzer se apaga por si mismo
	"""
	while (alertas['ALERTANDO'] and not alertas['NO_ALERTAR']):
                GPIO.output(PIN_BUZZER,1)
                sleep(1)
                GPIO.output(PIN_BUZZER,0)
                sleep(1)
	GPIO.output(PIN_BUZZER,0)

def activarAlertaSonora(alertas):
        """
        Esta funcion crea un thread para encender y apagar el buzzer
        """
	buzzer = threading.Thread(target=encenderBuzzer,args=(alertas,))
	buzzer.start()

def enviarAlertas(alertas,tipo_alerta,rom=0,temp=0,puerto=0):
        """
        Esta funcion se encarga de enviar una peticion http al servidor para
        que envie un mail al cliente con los datos correspondientes de la alerta
        """

	if (alertas["ALERTANDO"] and not alertas['NO_ALERTAR']):
		#Obtengo la APIKEY del usuario
		conf = open(PATH_CONF,"r")
		text_conf = conf.readlines()
		conf.close()
		apikey = text_conf[2].split(" ")[1][:-1]
		dispositivo = text_conf[0].split(" ")[1][:-1]

		#Configuro la url dependiendo del tipo de alerta
		if (tipo_alerta == "TEMP_ALTA"):
			data = "apikey=%s&dispositivo=%s&tipo_alerta=%s&temp=%s&rom=%s" % (apikey,dispositivo,tipo_alerta,temp,rom)

		elif (tipo_alerta == "TEMP_BAJA"):
			data = "apikey=%s&dispositivo=%s&tipo_alerta=%s&temp=%s&rom=%s" % (apikey,dispositivo,tipo_alerta,temp,rom)
	
		elif (tipo_alerta == "PUERTA"):
			data = "apikey=%s&dispositivo=%s&tipo_alerta=%s&puerto=%i" % (apikey,dispositivo,tipo_alerta,puerto)

		elif (tipo_alerta == "ALTERNA"):
			data = "apikey=%s&dispositivo=%s&tipo_alerta=%s&puerto=%i" % (apikey,dispositivo,tipo_alerta,puerto)	
	
		intentos = 0
		while (intentos < 5):
			try:
				ok = json.load(urllib2.urlopen("http://" + HOST_EMONCMS + "/bioguard/enviarAlertas.php",data=data,timeout=TIME_OUT))["enviado"]
				if (ok):
					break
				intentos += 1
			except:
				pass
