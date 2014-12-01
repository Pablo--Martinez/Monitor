#!/usr/bin/env python

"""
Este script solamente contiene las funciones que se engargan de las alertas locales
y las que seran luego enviadas al servidor para enviar un mail/mensaje/llamada al cliente
"""
import threading
from time import sleep
import RPi.GPIO as GPIO

PIN_BUZZER = 16

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

def enviarAlerta():
        """
        Esta funcion se encarga de enviar una peticion http al servidor para
        que envie un mail al cliente con los datos correspondientes de la alerta
        """
        pass

