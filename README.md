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
# Download files named 
- bt_rfid.py in Main addon folder
- pn532_i2c.py and main.py in Send to pico folder

Edit bt_rfid.py 
# ---------------- CONFIG ----------------
PICO_PORT = "/dev/ttyACM4"          # <-- adjust port for your pi
BAUD = 115200

The pico port can be find in your printer settings just like in photo

SPOOLMAN = "http://192.168.1.39:7912"  # <-- adjust for your spoolman ip adress 

- Send it to root folder of rpi same as in photo 

- After you did all the steps you will need to ssh to your pi, you can use putty same as me
- When you are connected to your printer you will need to add that service to startup and execute it using

  python3 ~/bt_rfid.py , the module should work now

  You will need to add a rule to execute this module every restart otherwise you will need to turn it manually each time
  How to do it :
  Create a service
  
  - sudo nano /etc/systemd/system/bt-rfid.service
  Paste everything from here
# - Paste
[Unit]
Description=Box Turtle RFID / NFC bridge
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/bin/python3 /home/pi/bt_rfid.py
Restart=always
RestartSec=2
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
# -  End
  
  
