#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
import threading

#eligiendo el modo de numeracion de los GPIO
GPIO.setmode(GPIO.BCM)

#Constantes del programa
PINES = [19,13,5,26,6,22]
LED_PUERTA = 12

#Configuro el pin de la alerta visual de la puerta
GPIO.setup(LED_PUERTA,GPIO.OUT)

#Path donde se encuentra el archivo de configuracion
PATH_CONF = "/home/pi/Monitor/rpi.conf"

def alertar():
	print "Alerta!"

def interrupcionPuerta(pin,tiempo_abierto):
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
			timer = threading.Timer(tiempo_abierto,alertar)
			timer.start()
			GPIO.output(LED_PUERTA,1)
		
		else:
			GPIO.wait_for_edge(pin, GPIO.FALLING)
			empezo = False
			time_end = time.time() - time_init
			print "Tiempo abierto: %f \n" % time_end
			timer.cancel()
			GPIO.output(LED_PUERTA,0)

def main(apikey,digitales,tiempo_apertura):
	 #Configuro el pin de la alerta visual de la puerta y lo seteo apagado
                GPIO.setup(LED_PUERTA,GPIO.OUT)
                GPIO.output(LED_PUERTA,0)

                for i in range(6):
                        if(digitales[i] != "NULL"):
                                if(digitales[i] == "Contacto"):
                                        t = threading.Thread(target=interrupcionPuerta,args=(PINES[i],tiempo_apertura))
                                        t.start()
                                else:
                                        #TODO
                                        pass

