#!/usr/bin/env python

import alertas
import threading
import leerTemperatura
import sensoresDigitales
import RPi.GPIO as GPIO

# Path donde se encuentra el archivo de configuracion
PATH_CONF = "/home/pi/Monitor/rpi.conf"

# Tiempo muerto en el que no alerta (sonora/mail) al cliente, en minutos
TIEMPO_MUERTO = 20

# pin donde esta ubicado el boton que reconoce las alertas
PIN_BOTON = 27

def reconocerAlertaBoton(channel,alertas):
	"""
	Esta funcion es la que acepta la interrucpion del boton para cancelar la alerta sonora
	"""
	#if(GPIO.input(PIN_BOTON) == 1 and alertas['ALERTANDO']):
	#	print "Desactivo"
	#	alertas['ALERTANDO'] = False
	#	alertas['NO_ALERTAR'] = True
	#	timer = threading.Timer(TIEMPO_MUERTO,reestablecerAlertar,args=(alertas,))
	#	timer.start()
	while(1):
		GPIO.wait_for_edge(channel,GPIO.RISING)
		if(GPIO.input(PIN_BOTON) == 1 and alertas['ALERTANDO']):
			alertas['ALERTANDO'] = False
	                alertas['NO_ALERTAR'] = True
	                timer = threading.Timer(TIEMPO_MUERTO,reestablecerAlertar,args=(alertas,))
	                timer.start()

def reestablecerAlertar(alertas):
	"""
	Esta funcion va a ser ejecutada con un timer que cuando es ejecutada luego de cierto tiempo
	solamente actualiza una variable global NO_ALERTAR que es usada para que no envie continuamente
	notificaciones de alerta al servidor
	"""
	alertas['NO_ALERTAR'] = False	
	print "NO_ALERTAR = FALSE"

def main():
	""" 
	Esta funcion se encarga de definir las variables globales, tomar los datos del archivo de configuracion
	y luego poner a ejecutar los scripts que se encargan de tomar las medidas de temperatura y los valores digitales
	"""
	
	try:
		# El diccionario ALERTAS posee dos campos, ALERTANDO que indica si el sistema esta en modo alerta
		# y NO_ALERTAR que indica que se recococio la alerta en el sistema y que no debe alertar por
		# un determinado periodo de tiempo
		ALERTAS = {'ALERTANDO':False, 'NO_ALERTAR':False}
	
		# Obtengo los datos del archivo de configuracion
	        conf = open(PATH_CONF,"r")
	        text_conf = conf.readlines()
	        conf.close()

		dispositivo = text_conf[0].split(" ")[1][:-1]
	        ciclo = int(text_conf[1].split(" ")[1][:-1])
	        apikey = text_conf[2].split(" ")[1][:-1]
	        minimo = float(text_conf[3].split(" ")[1][:-1])
	        maximo = float(text_conf[4].split(" ")[1][:-1])
		digitales = text_conf[5].split(" ")[1:-1]
                tiempo_apertura = int(text_conf[6].split(" ")[1][:-1])

		# Activo la interrupcion del boton que reconoce las alertas
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(PIN_BOTON, GPIO.IN)
		thread_boton = threading.Thread(target=reconocerAlertaBoton,args=(PIN_BOTON,ALERTAS))
		thread_boton.start()
		#GPIO.add_event_detect(PIN_BOTON, GPIO.RISING, callback=lambda x: reconocerAlertaBoton(PIN_BOTON,ALERTAS), bouncetime=500)

		# Configuro las alertas sonoras locales
		alertas.setupAlertas()

		# Thread encargado de tomar las medidas de temperatura
		thread_temperaturas = threading.Thread(target=leerTemperatura.leerTemperatura,args=(ciclo,apikey,minimo,maximo,ALERTAS))
		thread_temperaturas.start()

		# Thread encargado de los pines digitales
		thread_pines = threading.Thread(target=sensoresDigitales.sensoresDigitales,args=(dispositivo,apikey,digitales,tiempo_apertura,ALERTAS))
		thread_pines.start()
	
	except:
		GPIO.cleanup()
		exit

#Ejecuto el programa principal
if __name__ == "__main__":
	main()
