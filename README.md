# BOX-TURTLE-RFID-DETECTION
This addon add option for box turtle to have RFID Detection in each lane using PN532 Rfid modules
It uses avaiable port on BTIO for passing USB connection to the Rpi Pico for clean setup, it uses database from spoolman

BOM
Important, The mounts for rfid are only compatible Box Turtle 1.1 Trays, won't work with 1.0 without mods

- 1 PN532 Reader per lane
- 1 4 or 8 I2C mux for PICO for splitting PN532 Reader adresses because Rfid module PN532 have same I2C adress
- 1 RPI Pico flashed in micropython
  Here link how to do it, https://www.raspberrypi.com/documentation/microcontrollers/micropython.html
  
- Wires
- Type C to Type C or micro cable depends of your pico 


