#!/usr/bin/env python3

'''
INCLINOMETRO PARA EL TELESCOPIO DE 2.1M
Version 0.1-dev          16/Febrero/2023
Edgar Omar Cadena Zepeda
IA-UNAM-ENS
cadena@astro.unam.mx

Código para la lectura de un sensor Adafruit BNO055, utilizado como inclinometro,
en el telescopio de 2.1m.

El sensor se posiciona con las letras BNO055 del integrado apuntando al sur,
leidas desde el lado norte.

Cenit real tel 2m:
AH: 0.00
DEC: 31.02025

Default:
AH_offset: 0.00
DEC_offset: 0.00

Pasos:
Ajustar telescopio al cenit con nivel gota

Detener el programa principal con la siguiente instruccción:
sudo supervisorctl stop inclinometro2m

Ejecutar desde terminal el script python calibra_inclinometro2m.py

El script mide el valor actual del sensor promediando 100 mediciones y resta la diferencia con cenit real

Calcula el offset, lo guarda en el archivo de configuracion offset.json y luego el programa Inclinometro2m.py
lo esta restando siempre de sus mediciones para dar el valor calibrado.

Iniciar el programa principal con la siguiente instruccción:
sudo supervisorctl start inclinometro2m

Funciones Añadidas:
Ver. 0.1 - Implementada
'''

import sys
import time
import board
import serial
#import adafruit_bno055
from Adafruit_BNO055 import BNO055
import math
import simplejson as json


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


def calibra_inclinometro2m(iteraciones):
    xtempval = 0
    ytempval = 0
    ztempval = 0
    data = 0
    AH_offset = 0
    DEC_offset = 0

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
        angleXZ = angleXZ + 31.02025  # Latitud OAN-SPM
        DEC = angleXZ
    except:
        AH = 0
        DEC = 0
        print ("[*]ERROR - Mala lectura del sensor")
        pass

    AH_offset = 0 - AH
    DEC_offset = 31.02025 - DEC   # Latitud OAN-SPM

    # Data to be written
    dictionary = {
                'AH_offset': AH_offset,
                'DEC_offset': DEC_offset
                 }
    # Serializing json
    json_object = json.dumps(dictionary, separators=(',', ':'), sort_keys=True)
    # Writing to sample.json
    with open('/home/pi/Inclinometro2m/offset.json', 'w') as outfile:
        outfile.write(json_object)

    data = {'AH':AH, 'DEC':DEC, 'AH_offset':AH_offset, 'DEC_offset':DEC_offset}
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
    try:
        print("[+] Datos de Calibración Actuales:")
        with open('/home/pi/Inclinometro2m/offset.json') as jsonfile:
            content = json.load(jsonfile)
            print('AH_offset: {}'.format(content['AH_offset']))
            print('DEC_offset: {}'.format(content['DEC_offset']))
    except:
        print ("[*]ERROR - Sin archivo de calibración - Creandolo")
        pass
    time.sleep(0.2)
    input("[*] Press Enter to continue...")
    time.sleep(0.2)
    print("Calibrando Inclinometro2m {}".format(calibra_inclinometro2m(100)))
    time.sleep(0.2)
    print("[+] Sensor del Inclinometro Calibrado OK - Nuevos Offsets Almacenados")


except (KeyboardInterrupt, SystemExit): # If CTRL+C is pressed, exit cleanly:
    print ("Adios Viajero")
    sys.exit()
