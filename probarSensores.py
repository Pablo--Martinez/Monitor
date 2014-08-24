#!/usr/bin/env python

import os
import glob
from time import sleep

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

def read_temp_raw(path):
        f = open(path,'r')
        lines = f.readlines()
        f.close()
        return lines

def read_temp(path):
        lines = read_temp_raw(path)
        while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = read_temp_raw(path)
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                return temp_c

if __name__ == "__main__":
        while True:
		for i in range(len(glob.glob(base_dir + "28*"))):
                        path = glob.glob(base_dir + "28*")[i] + "/w1_slave"

                        #Leo la temperatura para ese sensor
                        temp = read_temp(path)

                        #Obtengo el nombre de ese feed para esa temperatura
                        feed_name = path[20:35].replace("-","")

                       	print feed_name + " " + str(temp)

                print "---------------------"
                sleep(1)

