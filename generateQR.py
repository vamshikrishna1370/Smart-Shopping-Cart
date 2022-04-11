import os
import sys

import qrcode
import numpy as np
# data to encode
data = ["http://192.168.1.97 ", " Mirchi_Powder"]
img = qrcode.make(str(data[0]))
img.save( "/Users/vamshikrishnareddyanireddy/Documents/Develop/QR_CodeScanner/TimeSavingShoppingCart/cartIP_finals_student.png")

img = qrcode.make(str(data[1]))
img.save( "/Users/vamshikrishnareddyanireddy/Documents/Develop/QR_CodeScanner/TimeSavingShoppingCart/Mirchi_Powder.jpg")
#filenames = ["Maggie", "Chocholate", "Rin", "Oil", "Daal", "Bread", "Masala", "Chilli_powder", "Rice", "Aata"]
#filename = "badam_123.png"
# instantiate QRCode object

# add data to the QR code
# for i in range(0, len(data)):
	#qr = qrcode.QRCode(version=1, box_size=10, border=4)
	#qr.add_data(str(data[i]))
	#qr.make()
	# img = qrcode.make(str(data[i]))
	# save img to a file
	# img.save( "cartIP.png")
	#img = qr.make_image(fill_color="white", back_color="black")
	#img.save("Images/"+str(data[i]) + ".png")
	