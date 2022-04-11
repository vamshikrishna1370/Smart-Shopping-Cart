import os
import sys
import csv
import qrcode
import cv2
import numpy as np
from RPLCD import i2c
from time import sleep
from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO

def InitializeLCDModule():
	# constants to initialise the LCD
	lcdmode = 'i2c'
	cols = 20
	rows = 4
	charmap = 'A00'
	i2c_expander = 'PCF8574'

	# Generally 27 is the address;Find yours using: i2cdetect -y 1 
	address = 0x27 
	port = 1 # 0 on an older Raspberry Pi

	# Initialise the LCD
	lcd = i2c.CharLCD(i2c_expander, address, port=port, charmap=charmap,
	                  cols=cols, rows=rows)
	lcd.backlight_enabled = True
	lcd.clear()
	lcd.crlf()
	lcd.write_string('Initializing LCD Setup...')
	lcd.crlf()
	lcd.write_string('                    ')
	lcd.crlf()
	lcd.write_string('                    ')
	return lcd


def DisplayTextOnLCD(lcd, ItemName, ItemPrice,  BillTotal):
	lcd.clear()
	lcd.write_string("{:<20}".format(ItemName))
	lcd.crlf()
	lcd.write_string("{:<8}".format("Price:-")  + "{:>12}".format("Rs."+ str(ItemPrice)))
	lcd.crlf()
	lcd.crlf()
	lcd.write_string("{:<8}".format("Total:-")  + "{:>12}".format("Rs."+ str(BillTotal)))
	return
def DisplayExactTextOnLCD(lcd, str1, str2, str3, str4):
	lcd.clear()
	lcd.write_string(str1)
	lcd.crlf()
	lcd.write_string(str2)
	lcd.crlf()
	lcd.write_string(str3)
	lcd.crlf()
	lcd.write_string(str4)
	return

def FetchInfoOfItem(data):
	#result = ["", "Item not found, rescan", "", "", ""]
	#print(result)
	ItemId =0.0
	ItemName = "NA"
	ItemPrice = 0.0
	for row in InventoryDB:
		#print("comparing it with "+ str(row[1]))
		if(str(data).strip() == str(row[1]).strip()):
			ItemId = int(str(row[0]).strip())
			ItemName = str(row[1]).strip()
			ItemPrice = float(str(row[2]).strip())
			print(ItemId, ItemName, ItemPrice)
	return ItemId, ItemName, ItemPrice


def UpdateCartContent(ItemId, ItemName, ItemPrice, shouldAddRemove, ItemsInCart, BillTotal):
	if(len(ItemsInCart)==1 and ItemsInCart[0][0]==None and (shouldAddRemove==True)):
		ItemsInCart = [[ItemId, ItemName, ItemPrice, 1, ItemPrice]]
		BillTotal = BillTotal + ItemPrice
	elif((len(ItemsInCart)== 0) and (shouldAddRemove==False)):
		print("Invalid Operation")
		return ItemsInCart, BillTotal
	else:
		for i in range(0,len(ItemsInCart)):
			if(ItemsInCart[i][0] == ItemId):
				if(shouldAddRemove == True):
					ItemsInCart[i][3] = ItemsInCart[i][3] + 1
					ItemsInCart[i][4] = ItemsInCart[i][4] + ItemsInCart[i][2]
					BillTotal = BillTotal + ItemPrice
					return ItemsInCart, BillTotal
				else:
					ItemsInCart[i][3] = ItemsInCart[i][3] - 1
					ItemsInCart[i][4] = ItemsInCart[i][4] - ItemsInCart[i][2]
					BillTotal = BillTotal - ItemPrice
					return ItemsInCart, BillTotal
		if(shouldAddRemove == True):
			ItemsInCart.append([ItemId, ItemName, ItemPrice, 1, ItemPrice])
			BillTotal = BillTotal + ItemPrice
		print("Billing total is :: " + str(BillTotal))
		return ItemsInCart, BillTotal

def ItemsInCartToString(ItemsInCart):
	ans=""
	#var b=[[1366, 'Bread', 32.0, 1, 32.0], [1368, 'Chilli_powder', 37.0, 1, 37.0], [1362, 'Chocholate', 5.45, 1, 5.45], [1361, 'Maggie', 12.0, 2, 24.0]];
	ans = ans + "var a=["
	for i in range(0,len(ItemsInCart)):
		ans = ans + "['"
		ans = ans + str(ItemsInCart[i][1]) + "', "
		ans = ans + "'"+str(ItemsInCart[i][0]) + "', "
		ans = ans + str(ItemsInCart[i][2]) + ", "
		ans = ans + str(ItemsInCart[i][3]) + ", "
		ans = ans + str(ItemsInCart[i][4]) 
		if(i == len(ItemsInCart)-1):
			ans = ans + "] "
		else:
			ans = ans + "], "
	ans = ans + "];"
	print(ans)
	return ans



def UpdateJSFile(fileName, ItemsInCart):
	# opening the file in read mode
	file = open(fileName, "r")
	replacement = ""
	# using the for loop
	for line in file:
		#print(line)
		line = line.strip()
		if("var a=" in line):
			changes = ItemsInCartToString(ItemsInCart)
			replacement = replacement + changes + "\n"
		else:
			replacement = replacement + line + "\n"
	file.close()
	# opening the file in write mode
	fout = open(fileName, "w")
	fout.write(replacement)
	fout.close()

def BeepBuzzer(Buzzer):
	GPIO.output(Buzzer, GPIO.HIGH)
	sleep(0.1)
	GPIO.output(Buzzer, GPIO.LOW)
	sleep(0.1)
	GPIO.output(Buzzer, GPIO.HIGH)
	sleep(0.2)
	GPIO.output(Buzzer, GPIO.LOW)
	sleep(0.1)
	GPIO.output(Buzzer, GPIO.HIGH)
	sleep(0.4)
	GPIO.output(Buzzer, GPIO.LOW)
	return 

InventoryDB = [[None]*5]
with open("/home/pi/Documents/TimeSavingShoppingCart/InventoryDB.csv") as csvFile:   #open the file
  CSVdata = csv.reader(csvFile, delimiter=',')  #read the data
  InventoryDB = list(CSVdata)
  for row in CSVdata:   #loop through each row
    print(row)          #print the data


Buzzer = 40
switch =38

GPIO.setmode(GPIO.BOARD)
GPIO.setup(Buzzer, GPIO.OUT)
GPIO.setup(switch, GPIO.IN)
NumItemsInInventory = len(InventoryDB)

ItemsInCart=[]
BillTotal = 0
frameCount =0
initflag = False
isAddRemove = True

#Initialize LCD Display by printing Initializing setup
lcd = InitializeLCDModule()


#Initialize Camera in the meanwhile
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
detector = cv2.QRCodeDetector()
# allow the camera to warmup
sleep(0.5)


DisplayExactTextOnLCD(lcd, "", "Initializing Camera...", "", "")
sleep(1)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	image = frame.array
	#cv2.imshow("Camera Preview", image)
	frameCount = frameCount +1
	if(frameCount > 100 and initflag == False):
		DisplayExactTextOnLCD(lcd, "", "Waiting for scan", "", "")
		initflag = True
	elif(initflag == False):
		rawCapture.truncate(0)
		continue

	data, bbox, _ = detector.detectAndDecode(image)
	print("Ready for next scan...")
	isAddRemove = bool(GPIO.input(switch))
	if bbox is not None:
		if data:
			print("[+] QR Code detected, data::", data)
			ItemId, ItemName, ItemPrice = FetchInfoOfItem(data)
			ItemsInCart, BillTotal = UpdateCartContent(ItemId, ItemName, ItemPrice, isAddRemove, ItemsInCart, BillTotal)
			DisplayTextOnLCD(lcd, ItemName, ItemPrice,  BillTotal)
			BeepBuzzer(Buzzer)
			print("Preset Content in the card is ::")
			print(ItemId, ItemName, ItemPrice, isAddRemove, ItemsInCart, BillTotal)
			UpdateJSFile("/var/www/html/demo.js", ItemsInCart)
			#os.system("sudo service apache2 restart & ")
			sleep(2)
	key = cv2.waitKey(1) & 0xFF
	key2 = cv2.waitKey(100)
	rawCapture.truncate(0)
	if ((key == ord("q")) or (key2 == 27)):
		lcd.clear()
		lcd.backlight_enabled = False
		cv2.destroyAllWindows()
		break
