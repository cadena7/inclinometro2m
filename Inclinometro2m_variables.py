#!/usr/bin/env python3

'''
INCLINOMETRO PARA EL TELESCOPIO DE 2.1M
Version 0.1-dev          10/Enero/2023
Edgar Omar Cadena Zepeda
IA-UNAM-ENS
cadena@astro.unam.mx

Código para la lectura de un sensor Adafruit BNO055, utilizado como inclinometro,
en el telescopio de 2.1m.

El sensor es leido mediante un código en lenguaje Python 3,
basado en una microcomputadora de la línea Raspberry Pi 3 modelo B.

El sensor se posiciona con las letras BNO055 del integrado apuntando al sur,
leidas desde el lado norte.


Funciones Añadidas:
Ver. 0.1 - Implementada
'''

#TAPA
class Variables():
    def __init__(self):
        # Entradas
        self.TAPA_NORTE_ABIERTA = 0
        self.TAPA_NORTE_CERRADA = 0
        self.TAPA_SUR_ABIERTA = 0
        self.TAPA_SUR_CERRADA = 0
        self.BUSCA_ABIERTO = 0
        self.BUSCA_CERRADO = 0

        # Salidas
        self.ABRE_BUSCADOR = 0
        self.CIERRA_BUSCADOR = 0
        self.ABRE_TAPA_NORTE = 0
        self.CIERRA_TAPA_NORTE = 0
        self.ABRE_TAPA_SUR = 0
        self.CIERRA_TAPA_SUR = 0

        # Variables extras
        self.TAPA_NORTE_STOP = 0
        self.TAPA_SUR_STOP = 0
        self.BUSCADOR_STOP = 0
