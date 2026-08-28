#!/usr/bin/env python3
import os
import schedule
import time

def reload_supervisor():
    # Ejecuta el comando con privilegios de superusuario
    os.system("sudo supervisorctl reload")

# Programa la tarea para que se ejecute todos los dias a las 4 AM
schedule.every().day.at("04:00").do(reload_supervisor)

# Programa la tarea para que se ejecute todos los dias a las 9 AM
schedule.every().day.at("09:00").do(reload_supervisor)

# Programa la tarea para que se ejecute todos los dias a las 1 PM
schedule.every().day.at("13:00").do(reload_supervisor)

# Programa la tarea para que se ejecute todos los dias a las 5 PM
schedule.every().day.at("17:00").do(reload_supervisor)

# Programa la tarea para que se ejecute todos los dias a las 9 PM
schedule.every().day.at("21:00").do(reload_supervisor)

# Programa la tarea para que se ejecute todos los dias a las 12 AM
schedule.every().day.at("00:00").do(reload_supervisor)

while True:
    # Ejecuta las tareas programadas
    schedule.run_pending()
    time.sleep(30)
