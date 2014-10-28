#!/usr/bin/env python

import pygtk
import datetime
from subprocess import call
from os import popen, remove, kill
pygtk.require("2.0")
import gtk
import gtk.glade
import psutil
import signal

PATH_CONF = "/home/pi/Monitor/rpi.conf"
SCRIPT_CONF = "/home/pi/Monitor/configurarEmoncms.py"
SCRIPT_LEER = "/home/pi/Monitor/leerTemperatura.py &"

def getCommandPID(command_name):
	# Funcion que me permite obtrener el PID de un proceso, particularmente para el de leerTemperatura.py
        for process in psutil.process_iter():
                if (len(process.cmdline) == 2) and (process.cmdline[1] == command_name):
                        return process.pid

class GUIError():
	def __init__(self,texto):
		error = gtk.MessageDialog(parent=None, flags=0, buttons=gtk.BUTTONS_OK)
		error.set_title("Error!")
		error.set_size_request(400,150)
		error.connect("delete-event", gtk.main_quit)
		label = gtk.Label(texto)
		error.vbox.pack_start(label)
		error.show_all()
		error.run()
		error.destroy()

class GUIConfiguracionBG():
	def __init__(self):
		self.gladefile = "GUIConfiguracion.glade" 
		self.glade = gtk.Builder()
		self.glade.add_from_file(self.gladefile)
		self.glade.connect_signals(self)
		self.glade.get_object("main").connect("delete-event", gtk.main_quit)
		self.funciones = {"iniciar": self.iniciar, 
				  "limpiar": self.limpiar,
				  "terminar": self.terminar,
				  "habilitarContacto": self.habilitarContacto,
				  "habilitarActualizarNombre": self.habilitarActualizarNombre,
				  "habilitarActualizarCiclo": self.habilitarActualizarCiclo,
				  "habilitarActualizarAPIKEY": self.habilitarActualizarAPIKEY,
				  "habilitarActualizarTemp": self.habilitarActualizarTemp,
				  "habilitarActualizarAlterna": self.habilitarActualizarAlterna,
				  "habilitarActualizarContacto": self.habilitarActualizarContacto,
				  "actualizar": self.actualizar}
			
		#Si existe el archivo de configuracion, se cargan los datos en la GUI				  
		try:
			conf = open(PATH_CONF,"r")
			text_conf = conf.readlines()
			nombre = text_conf[0].split(" ")[1][:-1]
			ciclo = int(text_conf[1].split(" ")[1][:-1])
			apikey = text_conf[2].split(" ")[1][:-1]
			minimo = float(text_conf[3].split(" ")[1][:-1])
			maximo = float(text_conf[4].split(" ")[1][:-1])
			pin_alterna = int(text_conf[5].split(" ")[1][:-1])
			pin_contacto = int(text_conf[6].split(" ")[1])
			tiempo_contacto = int(text_conf[6].split(" ")[2][:-1])
			conf.close()
			
			self.glade.get_object("terminar").set_sensitive(True)
			self.glade.get_object("iniciar").set_sensitive(False)
			self.glade.get_object("limpiar").set_sensitive(False)
			self.glade.get_object("nombre_valor").set_sensitive(False)
			self.glade.get_object("nombre_valor").set_text(nombre)
			self.glade.get_object("ciclo_valor").set_sensitive(False)
			self.glade.get_object("ciclo_valor").set_value(ciclo)
			self.glade.get_object("apikey_valor").set_sensitive(False)
			self.glade.get_object("apikey_valor").set_text(apikey)
			self.glade.get_object("min_valor").set_sensitive(False)
			self.glade.get_object("min_valor").set_value(minimo)
			self.glade.get_object("max_valor").set_sensitive(False)
			self.glade.get_object("max_valor").set_value(maximo)
			self.glade.get_object("alterna").set_sensitive(False)
			self.glade.get_object("pin_alterna").set_sensitive(False)
			self.glade.get_object("contacto").set_sensitive(False)
			self.glade.get_object("pin_contacto").set_sensitive(False)
			self.glade.get_object("tiempo_contacto").set_sensitive(False)
			self.glade.get_object("actualizar").set_sensitive(True)
	                self.glade.get_object("actualizar_nombre").set_sensitive(True)
	                self.glade.get_object("actualizar_ciclo").set_sensitive(True)
	                self.glade.get_object("actualizar_apikey").set_sensitive(True)
                	self.glade.get_object("actualizar_temp").set_sensitive(True)
        	        self.glade.get_object("actualizar_alterna").set_sensitive(True)
	                self.glade.get_object("actualizar_contacto").set_sensitive(True)
	
			if(pin_contacto != 0):
				self.glade.get_object("pin_contacto").set_active(pin_contacto - 1)
				self.glade.get_object("contacto").set_active(True)
				self.glade.get_object("tiempo_contacto").set_value(tiempo_contacto)
				self.glade.get_object("pin_contacto").set_sensitive(False)
				self.glade.get_object("tiempo_contacto").set_sensitive(False)
				
			if(pin_alterna != 0):
				self.glade.get_object("pin_alterna").set_active(pin_alterna - 1)
				self.glade.get_object("alterna").set_active(True)
				self.glade.get_object("pin_alterna").set_sensitive(False)
				
		#Si el archivo de configuracion no existe, la gui aparecera en blanco		
		except:
			self.glade.get_object("tiempo_contacto").set_sensitive(False)
			self.glade.get_object("pin_contacto").set_sensitive(False)
			self.glade.get_object("pin_alterna").set_sensitive(False)
			self.glade.get_object("terminar").set_sensitive(False)
		
	def iniciar(self,widget):
		nombre = self.glade.get_object("nombre_valor").get_text()
		if(nombre == ""):
			GUIError("Advertencia: verifique el nombre (alias) del dispositivo")
			return
			
		apikey = self.glade.get_object("apikey_valor").get_text()
		if(apikey == ""):
			GUIError("Advertencia: verifique su apikey")
			return
		
		ciclo = int(self.glade.get_object("ciclo_valor").get_value())
		minimo = float(self.glade.get_object("min_valor").get_value())
		maximo = float(self.glade.get_object("max_valor").get_value())
		
		if(minimo >= maximo):
			GUIError("Advertencia: Verifique los limites de temperatura")
			return
			
		if(self.glade.get_object("contacto").get_active() == True):
			pines_contacto = self.glade.get_object("pin_contacto")
			modelo = pines_contacto.get_model()
			pin_contacto = int(modelo[pines_contacto.get_active()][0])
			tiempo_contacto = self.glade.get_object("tiempo_contacto").get_value()
			if(tiempo_contacto == 0):
				GUIError("Advertencia: Verifique el tiempo de contacto abierto")			
				return
			
		else:
			tiempo_contacto = 0
			pin_contacto = 0
			
		if(self.glade.get_object("alterna").get_active() == True):
			pines_alterna = self.glade.get_object("pin_alterna")
			modelo = pines_alterna.get_model()
			pin_alterna = int(modelo[pines_alterna.get_active()][0])
		else:
			pin_alterna = 0
			
		if((pin_alterna != 0 and pin_contacto != 0) and (pin_alterna == pin_contacto)):
			GUIError("Advertencia: Verifique los pines de contacto y alterna")			
			return
			
		conf = open(PATH_CONF,"w")
		text_conf = "Nombre: %s\nCiclo: %i\nAPIKEY: %s\nMin: %f\nMax: %f\nAlterna: %i\nContacto: %i %i\n" % (nombre,ciclo,apikey,minimo,maximo,pin_alterna,pin_contacto,tiempo_contacto)
					
		conf.write(text_conf)
		conf.close()
		
		self.glade.get_object("terminar").set_sensitive(True)
		self.glade.get_object("iniciar").set_sensitive(False)
		self.glade.get_object("limpiar").set_sensitive(False)
		self.glade.get_object("nombre_valor").set_sensitive(False)
		self.glade.get_object("ciclo_valor").set_sensitive(False)
		self.glade.get_object("apikey_valor").set_sensitive(False)
		self.glade.get_object("min_valor").set_sensitive(False)
		self.glade.get_object("max_valor").set_sensitive(False)
		self.glade.get_object("alterna").set_sensitive(False)
                self.glade.get_object("pin_alterna").set_sensitive(False)
                self.glade.get_object("contacto").set_sensitive(False)
                self.glade.get_object("pin_contacto").set_sensitive(False)
                self.glade.get_object("tiempo_contacto").set_sensitive(False)
		self.glade.get_object("actualizar").set_sensitive(True)
		self.glade.get_object("actualizar_nombre").set_sensitive(True)
		self.glade.get_object("actualizar_ciclo").set_sensitive(True)
		self.glade.get_object("actualizar_apikey").set_sensitive(True)
		self.glade.get_object("actualizar_temp").set_sensitive(True)
		self.glade.get_object("actualizar_alterna").set_sensitive(True)
		self.glade.get_object("actualizar_contacto").set_sensitive(True)
		
		#Se ejecutan los scripts correspondientes
		#call(SCRIPT_CONF) #Primero se configura en el servidor
		#popen(SCRIPT_LEER) 		
		
	def limpiar(self,widget):
		self.glade.get_object("nombre_valor").set_text("")
		self.glade.get_object("apikey_valor").set_text("")
		self.glade.get_object("ciclo_valor").set_value(0)
		self.glade.get_object("min_valor").set_value(0)
		self.glade.get_object("max_valor").set_value(0)
		self.glade.get_object("tiempo_contacto").set_value(0)
		self.glade.get_object("tiempo_contacto").set_sensitive(False)
		self.glade.get_object("contacto").set_active(False)
		self.glade.get_object("alterna").set_active(False)
		self.glade.get_object("pin_contacto").set_sensitive(False)
		self.glade.get_object("pin_alterna").set_sensitive(False)
		
	def terminar(self,widget):
		self.glade.get_object("terminar").set_sensitive(False)
		self.glade.get_object("iniciar").set_sensitive(True)
		self.glade.get_object("limpiar").set_sensitive(True)
		self.glade.get_object("nombre_valor").set_sensitive(True)
		self.glade.get_object("ciclo_valor").set_sensitive(True)
		self.glade.get_object("apikey_valor").set_sensitive(True)
		self.glade.get_object("min_valor").set_sensitive(True)
		self.glade.get_object("max_valor").set_sensitive(True)
		self.glade.get_object("alterna").set_sensitive(True)
                self.glade.get_object("pin_alterna").set_sensitive(False)
                self.glade.get_object("contacto").set_sensitive(True)
                self.glade.get_object("pin_contacto").set_sensitive(False)
                self.glade.get_object("tiempo_contacto").set_sensitive(False)
		self.glade.get_object("actualizar").set_sensitive(False)
                self.glade.get_object("actualizar_nombre").set_sensitive(False)
                self.glade.get_object("actualizar_ciclo").set_sensitive(False)
		self.glade.get_object("actualizar_apikey").set_sensitive(False)
                self.glade.get_object("actualizar_temp").set_sensitive(False)
                self.glade.get_object("actualizar_alterna").set_sensitive(False)
                self.glade.get_object("actualizar_contacto").set_sensitive(False)

		#Elimino el archivo de configuracion
		remove(PATH_CONF)

		#Detengo el script que lee los datos
		pid = getCommandPID("./leerTemperatura.py")
		kill(pid,signal.SIGTERM)
				
	def habilitarContacto(self,widget):
		if(self.glade.get_object("contacto").get_active() == True):
			self.glade.get_object("tiempo_contacto").set_sensitive(True)
			self.glade.get_object("pin_contacto").set_sensitive(True)
		else:
			self.glade.get_object("tiempo_contacto").set_sensitive(False)
			self.glade.get_object("pin_contacto").set_sensitive(False)
			
	def habilitarAlterna(self,widget):
		if(self.glade.get_object("alterna").get_active() == True):
			self.glade.get_object("pin_alterna").set_sensitive(True)
		else:
			self.glade.get_object("pin_alterna").set_sensitive(False)

	def habilitarActualizarNombre(self,widget):
		if(self.glade.get_object("actualizar_nombre").get_active() == True):
			self.glade.get_object("nombre_valor").set_sensitive(True)
		else:
			self.glade.get_object("nombre_valor").set_sensitive(False)

	def habilitarActualizarCiclo(self,widget):
		if(self.glade.get_object("actualizar_ciclo").get_active() == True):
                        self.glade.get_object("ciclo_valor").set_sensitive(True)
                else:
                        self.glade.get_object("ciclo_valor").set_sensitive(False)

	def habilitarActualizarAPIKEY(self,widget):
		if(self.glade.get_object("actualizar_apikey").get_active() == True):
                        self.glade.get_object("apikey_valor").set_sensitive(True)
                else:
                        self.glade.get_object("apikey_valor").set_sensitive(False)

	def habilitarActualizarTemp(self,widget):
		if(self.glade.get_object("actualizar_temp").get_active() == True):
                        self.glade.get_object("max_valor").set_sensitive(True)
			self.glade.get_object("min_valor").set_sensitive(True)
                else:
                        self.glade.get_object("max_valor").set_sensitive(False)
			self.glade.get_object("min_valor").set_sensitive(False)

	def habilitarActualizarAlterna(self,widget):
		if(self.glade.get_object("actualizar_alterna").get_active() == True):
			self.glade.get_object("alterna").set_sensitive(True)
			self.habilitarAlterna(widget)
                else:
			self.glade.get_object("alterna").set_sensitive(False)
			self.glade.get_object("pin_alterna").set_sensitive(False)

	def habilitarActualizarContacto(self,widget):
		if(self.glade.get_object("actualizar_contacto").get_active() == True):
                        self.glade.get_object("contacto").set_sensitive(True)
			self.habilitarContacto(widget)
                else:
                        self.glade.get_object("contacto").set_sensitive(False)
			self.glade.get_object("pin_contacto").set_sensitive(False)
			self.glade.get_object("tiempo_contacto").set_sensitive(False)


	def actualizar(self,widget):
		#Obtengo los valores anteriores del archivo de configuracion
                conf = open(PATH_CONF,"r")
                text_conf = conf.readlines()
                nombre = text_conf[0].split(" ")[1][:-1]
                ciclo = int(text_conf[1].split(" ")[1][:-1])
                apikey = text_conf[2].split(" ")[1][:-1]
                minimo = float(text_conf[3].split(" ")[1][:-1])
                maximo = float(text_conf[4].split(" ")[1][:-1])
                pin_alterna = int(text_conf[5].split(" ")[1][:-1])
                pin_contacto = int(text_conf[6].split(" ")[1])
                tiempo_contacto = int(text_conf[6].split(" ")[2][:-1])
                conf.close()

		if(self.glade.get_object("actualizar_nombre").get_active()):
			nombre = self.glade.get_object("nombre_valor").get_text()
			
			if(nombre == ""):
        	                GUIError("Advertencia: verifique el nombre (alias) del dispositivo")
	                        return


		if(self.glade.get_object("actualizar_ciclo").get_active()):
			 ciclo = int(self.glade.get_object("ciclo_valor").get_value())

		if(self.glade.get_object("actualizar_apikey").get_active()):
			apikey = self.glade.get_object("apikey_valor").get_text()
			
			if(apikey == ""):
	                        GUIError("Advertencia: verifique su apikey")
        		        return

		if(self.glade.get_object("actualizar_temp").get_active()):
	                minimo = float(self.glade.get_object("min_valor").get_value())
        	        maximo = float(self.glade.get_object("max_valor").get_value())
			
			if(minimo >= maximo):
	                        GUIError("Advertencia: Verifique los limites de temperatura")
        	                return


		if(self.glade.get_object("actualizar_alterna").get_active()):
			if(self.glade.get_object("alterna").get_active() == True):
	                        pines_alterna = self.glade.get_object("pin_alterna")
	                        modelo = pines_alterna.get_model()
	                        pin_alterna = int(modelo[pines_alterna.get_active()][0])
	                else:
	                        pin_alterna = 0

		if(self.glade.get_object("actualizar_contacto").get_active()):
			if(self.glade.get_object("contacto").get_active() == True):
	                        pines_contacto = self.glade.get_object("pin_contacto")
	                        modelo = pines_contacto.get_model()
	                        pin_contacto = int(modelo[pines_contacto.get_active()][0])
	                        tiempo_contacto = self.glade.get_object("tiempo_contacto").get_value()

	                        if(tiempo_contacto == 0):
	                                GUIError("Advertencia: Verifique el tiempo de contacto abierto")
	                                return

        	        else:
                	        tiempo_contacto = 0
                        	pin_contacto = 0
	
		#Escribo los valores actualizados	
		conf = open(PATH_CONF,"w")
                text_conf = "Nombre: %s\nCiclo: %i\nAPIKEY: %s\nMin: %f\nMax: %f\nAlterna: %i\nContacto: %i %i\n" % (nombre,ciclo,apikey,minimo,maximo,pin_alterna,pin_contacto,tiempo_contacto)
                conf.write(text_conf)
                conf.close()

		#Desactivo los checkbox de actualizacion
		self.glade.get_object("nombre_valor").set_sensitive(False)
                self.glade.get_object("ciclo_valor").set_sensitive(False)
                self.glade.get_object("apikey_valor").set_sensitive(False)
                self.glade.get_object("min_valor").set_sensitive(False)
                self.glade.get_object("max_valor").set_sensitive(False)
                self.glade.get_object("alterna").set_sensitive(False)
                self.glade.get_object("pin_alterna").set_sensitive(False)
                self.glade.get_object("contacto").set_sensitive(False)
                self.glade.get_object("pin_contacto").set_sensitive(False)
                self.glade.get_object("tiempo_contacto").set_sensitive(False)
                self.glade.get_object("actualizar").set_sensitive(True)
                self.glade.get_object("actualizar_nombre").set_sensitive(True)
                self.glade.get_object("actualizar_ciclo").set_sensitive(True)
                self.glade.get_object("actualizar_apikey").set_sensitive(True)
                self.glade.get_object("actualizar_temp").set_sensitive(True)
                self.glade.get_object("actualizar_alterna").set_sensitive(True)
                self.glade.get_object("actualizar_contacto").set_sensitive(True)
		self.glade.get_object("actualizar_nombre").set_active(False)
                self.glade.get_object("actualizar_ciclo").set_active(False)
                self.glade.get_object("actualizar_apikey").set_active(False)
                self.glade.get_object("actualizar_temp").set_active(False)
                self.glade.get_object("actualizar_alterna").set_active(False)
                self.glade.get_object("actualizar_contacto").set_active(False)

		#Relanzo el script que lee los sensores
		pid = getCommandPID("./leerTemperatura.py")
		print pid
		kill(pid,signal.SIGTERM)
		popen(SCRIPT_LEER)

		
if __name__ == "__main__":
	GUIConfiguracionBG()
	gtk.main()
