#!/usr/bin/env python

import threading
import leerTemperatura
import sensorPuerta

#Path donde se encuentra el archivo de configuracion
PATH_CONF = "/home/pi/Monitor/rpi.conf"

def reconocerAlertaBoton(channel):
	"""
	Esta funcion es la que acepta la interrucpion del boton para cancelar la alerta sonora
	"""
	pass

def reestablecerAlertar():
	"""
	Esta funcion va a ser ejecutada con un timer que cuando es ejecutada luego de cierto tiempo
	solamente actualiza una variable global NO_ALERTAR que es usada para que no envie continuamente
	notificaciones de alerta al servidor
	"""
	
	pass

def main():
	""" 
	Esta funcion se encarga de definir las variables globales, tomar los datos del archivo de configuracion
	y luego poner a ejecutar los scripts que se encargan de tomar las medidas de temperatura y los valores digitales
	"""
	
	try:
	        conf = open(PATH_CONF,"r")
	        text_conf = conf.readlines()
	        conf.close()
	        ciclo = int(text_conf[1].split(" ")[1][:-1])
	        apikey = text_conf[2].split(" ")[1][:-1]
	        minimo = float(text_conf[3].split(" ")[1][:-1])
	        maximo = float(text_conf[4].split(" ")[1][:-1])
		digitales = text_conf[5].split(" ")[1:-1]
                tiempo_apertura = int(text_conf[6].split(" ")[1][:-1])

		#Thread encargado de tomar las medidas de temperatura
		thread_temperaturas = threading.Thread(target=leerTemperatura.leerTemperatura,args=(ciclo,apikey,minimo,maximo))
		thread_temperaturas.start()

		#Thread encargado de los pines digitales
		thread_pines = threading.Thread(target=sensorPuerta.main,args=(apikey,digitales,tiempo_apertura))
		thread_pines.start()
	
	except:
		exit

#Ejecuto el programa principal
if __name__ == "__main__":
	main()
