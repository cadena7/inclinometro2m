#!/usr/bin/env python3

'''
INCLINOMETRO PARA EL TELESCOPIO DE 2.1M
Version 0.2-dev          15/Febrero/2023
Edgar Omar Cadena Zepeda
IA-UNAM-ENS
cadena@astro.unam.mx

Código para la lectura de un sensor Adafruit BNO055, utilizado como inclinometro,
en el telescopio de 2.1m.

El sensor es leido mediante un código en lenguaje Python 3,
basado en una microcomputadora de la línea Raspberry Pi 3 modelo B.

El sensor se posiciona con las letras BNO055 del integrado apuntando al sur,
leidas desde el lado norte.

Solo ejecutalo con python3...

Funciones Añadidas:
Ver. 0.2 - Escribe datos en un archivo CSV
Ver. 0.1 - Implementada
'''


# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import sys
import time
import board
import serial
#import adafruit_bno055
from Adafruit_BNO055 import BNO055
import math
from datetime import timedelta
import csv

# If you are going to use I2C uncomment these lines
#i2c = board.I2C()
#sensor = adafruit_bno055.BNO055_I2C(i2c)

# If you are going to use UART uncomment these lines
#uart = serial.Serial("/dev/serial0")
#sensor = adafruit_bno055.BNO055_UART(uart)

sensor = BNO055.BNO055(serial_port='/dev/ttyS0')
# Enable verbose debug logging if -v is passed as a parameter.
if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
    logging.basicConfig(level=logging.DEBUG)
# Initialize the BNO055 and stop if something went wrong.
if not sensor.begin():
    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
# Print system status and self test result.
status, self_test, error = sensor.get_system_status()
print('System status: {0}'.format(status))
print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
# Print out an error if system status is in error mode.
if status == 0x01:
    print('System error: {0}'.format(error))
    print('See datasheet section 4.3.59 for the meaning.')
# Print BNO055 software revision and other diagnostic data.
sw, bl, accel, mag, gyro = sensor.get_revision()
print('Software version:   {0}'.format(sw))
print('Bootloader version: {0}'.format(bl))
print('Accelerometer ID:   0x{0:02X}'.format(accel))
print('Magnetometer ID:    0x{0:02X}'.format(mag))
print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))
# Read the Euler angles for heading, roll, pitch (all in degrees).
heading, roll, pitch = sensor.read_euler()
# Read the calibration status, 0=uncalibrated and 3=fully calibrated.
sys, gyro, accel, mag = sensor.get_calibration_status()
# Print everything out.
print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(
          heading, roll, pitch, sys, gyro, accel, mag))

header = ['AH', 'DEC']
column = []


def inclinometroPromediado(iteraciones):
    xtempval = 0
    ytempval = 0
    ztempval = 0
    data = 0
    valor_valido = 0
    max_allowed = 20
    attempt = 0

    while valor_valido != 1 or attempt <= max_allowed:
        valor_valido = 0
        attempt += 1

        for i in range(iteraciones):
            try:
                #data = sensor.acceleration
                data = sensor.read_accelerometer()
            except:
                data = 0
                print ("[*]ERROR - Mala lectura del sensor")
                pass
            xtempval = xtempval + data[0]
            ytempval = ytempval + data[1]
            ztempval = ztempval + data[2]
            time.sleep(0.01)

        x = xtempval / iteraciones
        y = ytempval / iteraciones
        z = ztempval / iteraciones

        try:
            angleYZ = math.atan( y / math.sqrt(x**2 + z**2))
            angleYZ = angleYZ*(180.0/math.pi) # Convierte de radianes a grados
            angleYZ = angleYZ/15
            AH = angleYZ
            #print(AH)
            if AH >= -5.00 and AH <= 5.00:
                valor_valido = valor_valido + 0.5

            angleXZ = math.atan(x / math.sqrt(y**2+z**2))
            angleXZ = angleXZ*(180.0/math.pi) # Convierte de radianes a grados
            angleXZ = angleXZ + 31.0440865  # Latitud OAN-SPM
            DEC = angleXZ
            #print(DEC)
            if DEC >= -90 and DEC <= 90:
                valor_valido = valor_valido + 0.5
        except:
            AH = 0
            DEC = 0
            print ("[*]ERROR - Mala lectura del sensor")
            pass

        h = int(AH)
        m = int((AH*60) % 60)
        s = int((AH*3600) % 60)
        if h >= 0:
            AHpretty = timedelta(hours=h, minutes=m, seconds=s)
        else:
            AHpretty = -timedelta(hours=h, minutes=m, seconds=s)
        AHpretty =  str(AHpretty)
        #print(valor_valido)

    #data = {'AH':AH, 'DEC':DEC, 'AHpretty':AHpretty}
    data = {'AH':AH, 'DEC':DEC}

    with open('/home/pi/Inclinometro2m/inclinometro2m.csv', mode='a', encoding='UTF8', newline='') as csvfile:
        column = [AH, DEC]
        writer_append  = csv.writer(csvfile)
        writer_append.writerow(column)

    return data



def inclinometroPromediado2(iteraciones):
    xtempval = 0
    ytempval = 0
    ztempval = 0
    data = 0

    for i in range(iteraciones):
        try:
            #data = sensor.acceleration
            data = sensor.read_accelerometer()
        except:
            data = 0
            print ("[*]ERROR - Mala lectura del sensor")
            pass
        xtempval = xtempval + data[0]
        ytempval = ytempval + data[1]
        ztempval = ztempval + data[2]
        time.sleep(0.01)

    x = xtempval / iteraciones
    y = ytempval / iteraciones
    z = ztempval / iteraciones

    try:
        angleYZ = math.atan( y / math.sqrt(x**2 + z**2))
        angleYZ = angleYZ*(180.0/math.pi) # Convierte de radianes a grados
        angleYZ = angleYZ/15
        AH = angleYZ

        angleXZ = math.atan(x / math.sqrt(y**2+z**2))
        angleXZ = angleXZ*(180.0/math.pi) # Convierte de radianes a grados
        angleXZ = angleXZ + 31.0440865  # Latitud OAN-SPM
        DEC = angleXZ
    except:
        AH = 0
        DEC = 0
        print ("[*]ERROR - Mala lectura del sensor")
        pass

    h = int(AH)
    m = int((AH*60) % 60)
    s = int((AH*3600) % 60)
    if h >= 0:
        AHpretty = timedelta(hours=h, minutes=m, seconds=s)
    else:
        AHpretty = -timedelta(hours=h, minutes=m, seconds=s)
    AHpretty =  str(AHpretty)

    #data = {'AH':AH, 'DEC':DEC, 'AHpretty':AHpretty}
    data = {'AH':AH, 'DEC':DEC}

    with open('/home/pi/Inclinometro2m/inclinometro2m.csv', mode='a', encoding='UTF8', newline='') as csvfile:
        column = [AH, DEC]
        writer_append  = csv.writer(csvfile)
        writer_append.writerow(column)

    return data


# El primer dato es basura, leerlo una vez para descartarlo
#sensor.acceleration    sensor.read_accelerometer()
def FirstInitSensor():
    print("[+] Primera lectura de prueba al sensor: {}".format(sensor.read_accelerometer()))
    time.sleep(.20)
    print("[+] Segunda lectura de prueba al sensor: {}".format(sensor.read_accelerometer()))
    time.sleep(.20)
    print("[+] Tercera lectura de prueba al sensor: {}".format(sensor.read_accelerometer()))
    time.sleep(.20)
    print("[+] Cuarta lectura de prueba al sensor: {}".format(sensor.read_accelerometer()))
    time.sleep(.20)
    print("[+] Quinta lectura de prueba al sensor: {}".format(sensor.read_accelerometer()))
    time.sleep(.20)
    print("[+] Sensor del Inclinometro Inicializado y Estabilizado")


try:
    FirstInitSensor()
    time.sleep(2)

    with open('/home/pi/Inclinometro2m/inclinometro2m.csv', mode='w', encoding='UTF8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)

    while True:
        time.sleep(0.5)
        print("Inclinometro2m DATA {}".format(inclinometroPromediado(1)))


except (KeyboardInterrupt, SystemExit): # If CTRL+C is pressed, exit cleanly:
    print ("Adios Viajero")
    sys.exit()
