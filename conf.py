"""
En este archivo se guardan todas las constantes de configuracion y demas
"""

# Pin donde se encuentra conectado el buzzer
PIN_BUZZER = 16

# URL del servidor en caso de que no se use la VPN
HOST_EMONCMS = "ec2-54-218-41-38.us-west-2.compute.amazonaws.com"

# IP del servidor en caso de que se use la VPN
#HOST_EMONCMS = "10.8.0.1"

# Path donde se encuentra el archivo de configuracion
PATH_CONF = "/home/pi/Monitor/rpi.conf"

# Tiempo muerto en el que no alerta (sonora/mail) al cliente, en minutos
TIEMPO_MUERTO = 20

# pin donde esta ubicado el boton que reconoce las alertas
PIN_BOTON = 27

# Ubicacion del archivo de configuracion del sistema
PATH_CONF = "/home/pi/Monitor/rpi.conf"

# En caso de falla de conexion, ubicacion del archivo de respaldo
PATH_LOG = "/home/pi/Monitor/perdidos.log"

# Path donde se guardan los respaldos de las alertas que no son enviadas
PATH_LOG_ALERTAS = "/home/pi/Monitor/alertas.log"

# Tiempo que se intenta mandar un dato al servidor, en segundos
TIME_OUT = 5

# GPIOs de los leds que indican fuera de temperatura
PIN_ALTA = 21
PIN_BAJA = 20

# GPIOs que son entradas digitales
PINES = [19,13,5,26,6,22]

# GPIO del led que indica apertura de puerta
LED_PUERTA = 12
