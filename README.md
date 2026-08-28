# Inclinómetro del telescopio de 2.1 m

Servicio de control para Raspberry Pi 3 que lee un sensor Bosch/Adafruit BNO055 por UART, calcula la posición aproximada del telescopio en ángulo horario (`AH`) y declinación (`DEC`), y controla las tapas del espejo primario y el buscador mediante GPIO.

El programa expone un servidor TCP en el puerto `4545`. Los comandos y respuestas usan texto plano y JSON para conservar compatibilidad con la electrónica anterior del telescopio.

## Características

- Lectura del BNO055 mediante `/dev/ttyS0` a 115200 baud.
- BNO055 en modo `ACCONLY`, sin deriva causada por el algoritmo de fusión NDOF.
- Acceso exclusivo al UART para evitar que dos clientes mezclen respuestas serie.
- Mediana de muestras para reducir valores aislados y vibraciones.
- Lectura válida mientras el telescopio está en movimiento.
- Recuperación automática del BNO055 después de errores UART consecutivos.
- Calibración por comando y almacenamiento de offsets en `offset.json`.
- Control y monitoreo de tapas y buscador mediante GPIO.
- Límites de tiempo para apagar los motores de forma automática.
- Compatible con un sistema raíz protegido mediante overlay readonly.

## Hardware previsto

- Raspberry Pi 3 Model B.
- Sensor Adafruit/Bosch BNO055 conectado por UART.
- Electrónica de potencia para los motores de tapas y buscador.
- Interruptores de límite conectados a entradas GPIO de 3.3 V.

El BNO055 se instala con las letras del integrado apuntando hacia el sur, legibles desde el lado norte.

> **Importante:** los GPIO de la Raspberry Pi trabajan a 3.3 V. No conectes señales de 5 V directamente.

## Asignación GPIO

La numeración utilizada es BCM.

| Función | GPIO | Tipo |
|---|---:|---|
| Tapa norte abierta | 5 | Entrada con pull-down |
| Tapa norte cerrada | 6 | Entrada con pull-down |
| Tapa sur abierta | 13 | Entrada con pull-down |
| Tapa sur cerrada | 26 | Entrada con pull-down |
| Buscador abierto | 23 | Entrada con pull-down |
| Buscador cerrado | 24 | Entrada con pull-down |
| Abrir buscador | 4 | Salida |
| Cerrar buscador | 17 | Salida |
| Abrir tapa norte | 27 | Salida |
| Cerrar tapa norte | 22 | Salida |
| Abrir tapa sur | 10 | Salida |
| Cerrar tapa sur | 9 | Salida |

La secuencia de operación implementada es:

- Apertura: primero tapa norte, después tapa sur.
- Cierre: primero tapa sur, después tapa norte.

## Configuración de UART en Raspberry Pi 3

El programa utiliza directamente:

```text
/dev/ttyS0
```

En `/boot/config.txt` debe estar habilitado el UART:

```ini
[all]
enable_uart=1
```

La consola serie no debe usar `ttyS0`. La configuración se puede verificar sin modificar el sistema:

```bash
readlink -f /dev/serial0
ls -l /dev/serial0 /dev/ttyS0 /dev/ttyAMA0
cat /proc/cmdline
systemctl is-enabled serial-getty@ttyS0.service
systemctl is-active serial-getty@ttyS0.service
```

El resultado esperado es:

- `/dev/serial0` apunta a `/dev/ttyS0`.
- `/proc/cmdline` no contiene `console=ttyS0` ni `console=serial0`.
- `serial-getty@ttyS0.service` está `disabled` e `inactive`.

Para deshabilitar el servicio si estuviera activo:

```bash
sudo systemctl disable --now serial-getty@ttyS0.service
```

Después de modificar la configuración de arranque es necesario reiniciar la Raspberry Pi.

## Instalación

Clona o copia el proyecto en la ruta utilizada por la configuración de Supervisor:

```bash
cd /home/pi
git clone URL_DEL_REPOSITORIO Inclinometro2m
cd /home/pi/Inclinometro2m
```

Instala las dependencias del sistema y de Python:

```bash
sudo apt update
sudo apt install -y python3 python3-pip supervisor netcat-openbsd
python3 -m pip install pyserial simplejson RPi.GPIO Adafruit-GPIO adafruit-blinka schedule
```

La biblioteca `Adafruit_Python_BNO055` está incluida en el repositorio y se importa directamente desde la carpeta del proyecto.

Comprueba que el usuario `pi` pertenezca al grupo `dialout`:

```bash
groups pi
```

Si no aparece `dialout`:

```bash
sudo usermod -aG dialout pi
```

Después cierra la sesión y vuelve a entrar, o reinicia el equipo.

## Ejecución manual

Detén primero cualquier instancia administrada por Supervisor, porque solo un proceso puede utilizar el puerto `4545` y `/dev/ttyS0`:

```bash
sudo supervisorctl stop inclinometro2m
cd /home/pi/Inclinometro2m
python3 Inclinometro2m.py
```

Un arranque correcto en modo `ACCONLY` puede mostrar:

```text
System status: 6
Self test result (0x0F is normal): 0x0F
Heading=0.00 Roll=0.00 Pitch=0.00 Sys_cal=0 Gyro_cal=0 Accel_cal=0 Mag_cal=0
```

Los ángulos Euler y estados de calibración en cero son normales en `ACCONLY`; el programa calcula `AH` y `DEC` directamente a partir del acelerómetro.

## Instalación con Supervisor

El repositorio incluye una configuración de ejemplo en `Instalador en Raspi/supervisor/conf.d/main.conf`.

```bash
sudo cp reinicio_supervisor.py /home/pi/reinicio_supervisor.py
sudo cp "Instalador en Raspi/supervisor/conf.d/main.conf" /etc/supervisor/conf.d/inclinometro2m.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start inclinometro2m
sudo supervisorctl status inclinometro2m
```

La configuración incluida envía `stdout` y `stderr` a `/dev/null`, por lo que no genera archivos de log.

> La configuración actual contiene también `reinicio_supervisor.py`, un mecanismo histórico de reinicios programados, y espera encontrarlo directamente en `/home/pi`. Conviene conservarlo durante las primeras pruebas prolongadas y retirarlo solo después de confirmar estabilidad durante 24–48 horas.

## Comandos TCP desde la misma Raspberry Pi

Todos los ejemplos siguientes se pueden copiar y pegar directamente en otra terminal de la Raspberry Pi.

### Lectura rápida

Aunque se solicita una lectura, internamente se usan al menos cinco muestras:

```bash
printf 'DATA\n' | nc 127.0.0.1 4545
```

### Lectura filtrada

El número de muestras queda limitado al intervalo de 1 a 100; internamente se utilizan al menos cinco.

```bash
printf 'INCLINOMETRO 1\n' | nc 127.0.0.1 4545
printf 'INCLINOMETRO 10\n' | nc 127.0.0.1 4545
printf 'INCLINOMETRO 100\n' | nc 127.0.0.1 4545
```

Respuesta normal:

```json
{"AH":0.0012,"DEC":31.0204}
```

Si la lectura y la recuperación del sensor fallan:

```json
{"ERROR":"SENSOR"}
```

### Consultar offsets

```bash
printf 'OFFSETS\n' | nc 127.0.0.1 4545
```

### Calibrar

Coloca primero el telescopio exactamente en el cenit y luego ejecuta:

```bash
printf 'CALIBRA\n' | nc 127.0.0.1 4545
```

`CALIBRA` toma 100 muestras y sobrescribe inmediatamente `/home/pi/Inclinometro2m/offset.json`.

- Con el overlay readonly activo, la calibración funciona durante la sesión pero desaparece al reiniciar.
- Fuera del overlay, la calibración queda almacenada de forma persistente.

### Estado de tapas y buscador

```bash
printf 'STATUS\n' | nc 127.0.0.1 4545
```

También se acepta `ESTADO`.

## Comandos de motores

> **Precaución:** estos comandos accionan motores reales. Ejecútalos únicamente cuando el área y el telescopio estén en condiciones seguras.

| Acción | Comando local |
|---|---|
| Abrir tapas y buscador | `printf 'OPENALL\n' \| nc 127.0.0.1 4545` |
| Cerrar tapas y buscador | `printf 'CLOSEALL\n' \| nc 127.0.0.1 4545` |
| Abrir tapas | `printf 'OPENTAPAS\n' \| nc 127.0.0.1 4545` |
| Cerrar tapas | `printf 'CLOSETAPAS\n' \| nc 127.0.0.1 4545` |
| Abrir buscador | `printf 'OPENBUSCA\n' \| nc 127.0.0.1 4545` |
| Cerrar buscador | `printf 'CLOSEBUSCA\n' \| nc 127.0.0.1 4545` |
| Apagar todos los motores | `printf 'STOP\n' \| nc 127.0.0.1 4545` |

También se conservan los comandos heredados `:ABRIR;`, `:CERRAR;`, `:AB;`, `:CB;` y `:?TA;`.

Los actuadores tienen los siguientes tiempos máximos de energización:

- Tapas: 25 segundos.
- Buscador: 4 segundos.

## Lecturas durante movimiento

El programa distingue entre una lectura estable, una lectura plausible durante movimiento y un error real de UART:

- Magnitud entre 7 y 13 m/s²: se considera estable y tiene preferencia.
- Magnitud entre 2 y 20 m/s²: se considera plausible durante movimiento.
- Valores incompletos, no numéricos, infinitos o fuera del margen plausible: se descartan.
- El sensor solo se reinicializa cuando faltan datos y ocurrieron al menos tres excepciones UART.

Durante una aceleración o frenado, la posición puede presentar un error momentáneo porque un acelerómetro no puede separar perfectamente la gravedad de la aceleración lineal. La mediana reduce valores aislados, pero no elimina esta limitación física.

## Seguridad de red

El servidor escucha en todas las interfaces mediante `0.0.0.0:4545` y no implementa autenticación ni cifrado. Algunos comandos accionan motores. El puerto debe limitarse a una red de control confiable mediante firewall o segmentación de red; no debe exponerse a Internet.

## Archivos principales

| Archivo | Propósito |
|---|---|
| `Inclinometro2m.py` | Servicio principal, sensor, TCP, GPIO y motores |
| `Inclinometro2m_variables.py` | Estado compartido de GPIO y actuadores |
| `offset.json` | Offsets actuales de AH y DEC |
| `calibra_inclinometro2m.py` | Utilidad histórica de calibración manual |
| `test_sensor.py` | Prueba independiente del BNO055 |
| `reinicio_supervisor.py` | Reinicios históricos programados de Supervisor |
| `Instalador en Raspi/` | Configuraciones de instalación y Supervisor |
| `Adafruit_Python_BNO055/` | Biblioteca BNO055 incluida |
| `backups/` | Copias anteriores del servicio principal |

## Restaurar una versión respaldada

Antes de las mejoras de estabilidad se guardaron copias completas en `backups/`. Para restaurar una de ellas, detén primero el servicio y copia explícitamente el archivo deseado:

```bash
sudo supervisorctl stop inclinometro2m
cp backups/Inclinometro2m.py.pre_movimiento_20260809 Inclinometro2m.py
sudo supervisorctl start inclinometro2m
```

## Autor

Edgar Omar Cadena Zepeda  
Instituto de Astronomía, UNAM — Ensenada  
`cadena@astro.unam.mx`

## Licencia

El código principal de este proyecto todavía no declara una licencia. La biblioteca incluida `Adafruit_Python_BNO055` conserva su propia licencia MIT. Antes de aceptar contribuciones o reutilización externa, se recomienda añadir una licencia explícita para el proyecto principal.
