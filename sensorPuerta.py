#!/usr/bin/env python

import time
import RPi.GPIO as GPIO

#eligiendo el modo de numeracion de los GPIO
GPIO.setmode(GPIO.BCM)

#configurando pin 23 BCM como entrada con pull_down
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)


#ISR de la interrupcion por flanco en pin 23
def isrPin23(channel):
	global empezo
	global alerta
	global time_init
	if not empezo:
		GPIO.remove_event_detect(23)
		GPIO.add_event_detect(23, GPIO.BOTH, callback=isrPin23, bouncetime=200)
		time_init = time.time()
		empezo = True 
		print "Inicio: %f" % time_init
	else:
		GPIO.remove_event_detect(23)
                GPIO.add_event_detect(23, GPIO.BOTH, callback=isrPin23, bouncetime=200)		
		empezo = False
		alerta = False
		print "Tiempo: %f" % float(time.time() - time_init)		


if __name__ == "__main__":
	#configurando handler de INT por flanco ascendente pin 23
	GPIO.add_event_detect(23, GPIO.BOTH, callback=isrPin23, bouncetime=2000)

	#definnicion de variables globales
	global time_init
	
	global empezo
	empezo = False
	
	global alerta
	alerta = False

	#bucle pricnipal de ejecucion
	print("\n ...Iniciando el programa...\n\n")
	while True:
		if empezo:
			if (not alerta and (int(time.time() - time_init) > 5)):
				alerta = True
				print "Alerta!"	
	GPIO.cleanup()
