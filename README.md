# BOX-TURTLE-RFID-DETECTION
Be aware my first language is not english so it might be some errors ! Thanks

This addon add option for box turtle to have RFID Detection in each lane using PN532 Rfid modules
It uses avaiable port on BTIO for passing USB connection to the Rpi Pico for clean setup, it uses database from spoolman

BOM
Important, The mounts for rfid are only compatible Box Turtle 1.1 Trays, won't work with 1.0 without mods

- 1 PN532 Reader per lane
- 1 4 or 8 I2C mux for PICO for splitting PN532 Reader adresses and better wiring it's using Qwicc connectors

- 1 RPI Pico flashed in micropython
  Here link how to do it, https://www.raspberrypi.com/documentation/microcontrollers/micropython.html
  
- Wires
- Type C to Type C or micro cable depends of your pico

# ---------------- Printing ----------------
Left side middle x3 
Right side middle x3
Right side Right side x1
left side Right side x1

# -- Wiring section -- 
Connect readers in your mux, use port 0-1-2-3 on mux , the 4-5-6-7 ports if using 8 channel mux doesn't work so be aware
Be sure to switch to I2C mode in your readers

Check if your wires have enough length for each lane !
<img width="421" height="435" alt="Screenshot_5" src="https://github.com/user-attachments/assets/60f162fb-ab93-44a7-98c5-fe1d8b696aa3" />

Connect mux to pico I2C port then pico to rpi via usb

# Download files named 
- bt_rfid.py in Main addon folder
- btrfid.service.txt file
- pn532_i2c.py and main.py in Send to pico folder

Edit bt_rfid.py 
# ---------------- CONFIG ----------------
PICO_PORT = "/dev/pico-nfc"          # <-- adjust port for your pi
BAUD = 115200

The pico port can be find in your printer settings just like in photo

<img width="614" height="530" alt="Screenshot_1" src="https://github.com/user-attachments/assets/2aba368c-6f93-4eab-89f7-e32bff1c0d1f" />

SPOOLMAN = "http://192.168.1.39:7912"  # <-- adjust for your spoolman ip adress 

- Send it to root folder of rpi same as in photo 

<img width="771" height="507" alt="Screenshot_2" src="https://github.com/user-attachments/assets/e4d5294e-633c-4ac1-8d67-385a5f1c80f2" />


- After you did all the steps you will need to ssh to your pi, you can use putty same as me
- When you are connected to your printer you will need to add that service to startup and execute it using

  - python3 ~/bt_rfid.py
  - the module should work now

  You will need to add a rule to execute this module every restart otherwise you will need to turn it manually each time
  - How to do it :
  - Create a service using :
  - sudo nano /etc/systemd/system/bt-rfid.service
  - Paste everything from btrfid.service.txt file
  Save and exit

  Enable and start
- sudo systemctl daemon-reload
- sudo systemctl enable bt-rfid.service
- sudo systemctl start bt-rfid.service

After you did everything mentioned before now you can send main.py and i2c module using mpremote
I have my pico in ACM4 port but your can be different so ajust for your setup

- mpremote connect /dev/ttyACM4 fs cp pn532_i2c.py :pn532_i2c.py
- mpremote connect /dev/ttyACM4 fs cp main.py :main.py
- mpremote connect /dev/ttyACM4 reset

# ---Bind Pico to pico-nfc port---
1️⃣ Plug the Pico and find its current port
ls /dev/ttyACM*

Example output:

/dev/ttyACM4
2️⃣ Get Pico USB identifiers
udevadm info -a -n /dev/ttyACM4 | grep '{idVendor}\|{idProduct}\|{serial}' -m3

Example result:

ATTRS{idVendor}=="2e8a"
ATTRS{idProduct}=="0005"
ATTRS{serial}=="4250304638303305"

Those values identify the Raspberry Pi Pico.

3️⃣ Create udev rule

Open the rules file:

sudo nano /etc/udev/rules.d/99-pico-nfc.rules

Put exactly this (adjust serial if yours is different):

SUBSYSTEM=="tty", ATTRS{idVendor}=="2e8a", ATTRS{idProduct}=="0005", ATTRS{serial}=="4250304638303305", SYMLINK+="pico-nfc"

Save.

4️⃣ Reload rules
sudo udevadm control --reload-rules
sudo udevadm trigger

Done, you have bind the pico to PICO_PORT = "/dev/pico-nfc", use it in bt_rfid.py if not done before

# -- Spoolman Section -- 

In order to communicate with our pico you need to have database and extra section in each spool which is used by our pico 

- To add you will need to add custom section in spoolman settings like in photo, the name need to be same as mine if not it will not work at all
  <img width="1892" height="778" alt="Screenshot_3" src="https://github.com/user-attachments/assets/a788b8c6-d20b-45d8-b596-578bf9030e6c" />
When you will be adding your spool in spoolman search on bottom for that external_id section

<img width="1652" height="745" alt="Screenshot_4" src="https://github.com/user-attachments/assets/5bb9072c-72bd-4ab0-8895-de766be852e3" />

Here you will need to insert unique id assigned to nfc tag, to do just scan the tag even if not in database and copy the numbers from console in mainsail to that section to assign the "Tag" to that spool 

Then each time you will pass your tag the spool will be assigned to lane 

# -- Assembly section -- 

Assembly each reader same as in photo 

![20260111_203220](https://github.com/user-attachments/assets/c49bcb0e-fc20-40f8-a526-bbd5a1bafbf5)

Insert each reader same as in photo between each lane 
![20260111_203506](https://github.com/user-attachments/assets/feb57071-71fa-4aea-b5d2-3dd5367c60f8)

Mount the mux in middle of trays, you can use motor mount for mounting 1 screw but if your wires are longer than mine just fix it directly on extrusion, as before connect mux to rpi pico and rpi pico in type c port in BTIO for clean wiring ( Works if you are using CAN not USB for BoxTurtle Motherboard ) , then connect your box turtle as usual and add type c cable from your printer to BTIO type C connector 

<img width="1652" height="745" alt="Screenshot_4" src="https://github.com/Kr3jzolPL/BOX-TURTLE-RFID-DETECTION/blob/main/photos./20260312_144841.jpg" />

<img width="1652" height="745" alt="Screenshot_4" src="https://github.com/Kr3jzolPL/BOX-TURTLE-RFID-DETECTION/blob/main/photos./20260312_144845.jpg" />

Check if everything works by inserting the spool with tag 

<img width="1652" height="745" alt="Screenshot_4" src="https://github.com/Kr3jzolPL/BOX-TURTLE-RFID-DETECTION/blob/main/photos./20260312_144815.jpg" />
