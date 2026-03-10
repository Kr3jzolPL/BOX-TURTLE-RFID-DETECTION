# BOX-TURTLE-RFID-DETECTION
Be aware my first language is not english so it might be some errors ! Thanks

This addon add option for box turtle to have RFID Detection in each lane using PN532 Rfid modules
It uses avaiable port on BTIO for passing USB connection to the Rpi Pico for clean setup, it uses database from spoolman

BOM
Important, The mounts for rfid are only compatible Box Turtle 1.1 Trays, won't work with 1.0 without mods

- 1 PN532 Reader per lane
- 1 4 or 8 I2C mux for PICO for splitting PN532 Reader adresses and better wiring

- 1 RPI Pico flashed in micropython
  Here link how to do it, https://www.raspberrypi.com/documentation/microcontrollers/micropython.html
  
- Wires
- Type C to Type C or micro cable depends of your pico 

How to install 

Download file named bt_rfid.py

edit it and only edit these lines 

---------------- CONFIG ----------------
PICO_PORT = "/dev/ttyACM4"          # <-- adjust port for your pi
BAUD = 115200

SPOOLMAN = "http://192.168.1.39:7912"  # <-- adjust for your spoolman ip adress 
