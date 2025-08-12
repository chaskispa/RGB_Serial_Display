# Color Serial Display

Este proyecto lee datos de color RGB enviados por puerto serial (desde un Arduino o un Beetle CJMCU) y muestra ese color a pantalla completa en una Raspberry Pi. La configuración permite duplicar la salida en dos pantallas HDMI, lo que lo hace ideal para instalaciones o montajes que requieren retroalimentación visual sincronizada.

## Características

- Lee valores RGB con formato `#RGB#` por puerto serial
- Muestra color a pantalla completa en una o dos pantallas HDMI
- Muestra pantalla de "iniciando" si no hay datos aún
- Se reinicia automáticamente si falla
- Soporte opcional para duplicar la imagen con `xrandr` (modo espejo)

## Requisitos de hardware

- Raspberry Pi 4 (u otro modelo compatible)
- Beetle CJMCU (u otro dispositivo que envíe datos por serial)
- 1 o 2 pantallas HDMI (idealmente una de 1024x600)
- Tarjeta SD con Raspberry Pi OS (se recomienda la versión con escritorio)

## Formato del mensaje serial

El script espera recibir datos con el siguiente formato:
`#<r><g><b>#`

Donde:
- `<r>`, `<g>`, `<b>` son bytes individuales (valores de 0 a 255) que representan rojo, verde y azul.
- El mensaje debe comenzar y terminar con `#` y contener **exactamente 3 bytes** entre medio.

## Instalación

### 1. Instalar dependencias

```bash
sudo apt update
sudo apt install -y python3 python3-pip openbox xinit xserver-xorg x11-xserver-utils
pip3 install pygame pyserial
```
### 2. Habilitar inicio automático con escritorio (X11)
Configura la Raspberry Pi para que inicie sesión automáticamente y cargue el entorno gráfico:
```bash
sudo raspi-config
# → Opciones del sistema → Arranque → B2: Autologin en consola
```
Luego agrega `startx` al final de tu `~/.bashrc`:
```bash
echo "if [ -z \"$DISPLAY\" ] && [ \"$(tty)\" = \"/dev/tty1\" ]; then startx; fi" >> ~/.bashrc
```
### 3. Guardar el script principal
Guarda el archivo como `/home/pi/color_serial_display.py`.

### 4. Configurar el espejo de pantallas
Crea el archivo `/home/pi/mirror-setup.sh` con este contenido:
```bash
#!/bin/bash
export DISPLAY=:0
sleep 5
xrandr --newmode "1024x600_60.00" 49.00 1024 1072 1168 1312 600 603 613 624 -hsync +vsync 2>/dev/null
xrandr --addmode HDMI-2 1024x600_60.00 2>/dev/null
xrandr --output HDMI-1 --mode 1024x600 --primary
xrandr --output HDMI-2 --mode 1024x600_60.00 --same-as HDMI-1
```
Hazlo ejecutable:
```bash
chmod +x /home/pi/mirror-setup.sh
```

### 5. Configurar Openbox para iniciar el script
```bash
# Evitar que la pantalla se apague
xset s off &
xset -dpms &
xset s noblank &

# Ejecutar configuración de espejo
/home/pi/mirror-setup.sh &

# Iniciar el script con reinicio automático
bash -c 'until python3 /home/pi/color_serial_display.py; do echo "[DEBUG] Script crashed. Restarting in 2s..."; sleep 2; done' >> /home/pi/color_display.log 2>&1 &
```
### 6. Asegurar que Openbox se inicie con X
Edita el archivo `/home/pi/.xinitrc`:
```bash
exec openbox-session
```

## Uso
Al arrancar, la Raspberry Pi:
1. Inicia sesión automática en consola
2. Ejecuta `startx`, que carga Openbox
3. Ejecuta el script `mirror-setup.sh` que configura el espejo de pantalla
4. nicia el script de color que:
   * Espera datos por serial
   * Muestra color a pantalla completa cuando recibe un valor RGB
   * Reinicia si hay errores

## Logs
El registro de salida y errores se guarda en:
```
/home/pi/color_display.log
```
Puedes revisar ese archivo para diagnosticar problemas de conexión o errores del script.


   
