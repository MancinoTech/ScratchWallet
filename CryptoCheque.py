#Generate new Scratch Wallets
import bitcoinlib
from bitcoinlib.mnemonic import Mnemonic
import ecdsa
import qrcode
import codecs
import hashlib
import base58
import base64
import io
import bitcoin
import binascii
import secrets
import datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont

barcode = []

def convertSNtoCoordinates(sn, w, h):
      #extend the serial number to build more shapes
  hash = hashlib.sha256(sn.encode()).hexdigest()
  seed = [int(c, 16) for c in hash]

  # Split the array into 4 equal arrays
  x1 = np.array_split(seed, 4)[0]
  x2 = np.array_split(seed, 4)[1]
  y1 = np.array_split(seed, 4)[2]
  y2 = np.array_split(seed, 4)[3]

  #Expand the hex out to the width and height variables
  wMultiplier = w*1.2/16
  hMultiplier = h*1.2/16
  
  for n in range(len(x1)):
    #sort coordinates so x1 is always smaller than x2
    if x1[n] > x2[n]:
        holder = x2[n]
        x2[n] = x1[n]
        x1[n] = holder
    #sort coordinates so y1 is always smaller than y2
    if y1[n] > y2[n]:
        holder = y2[n]
        y2[n] = y1[n]
        y1[n] = holder
    #spread the circle coordinates out so the drawer doesn't end up drawing lines
    wDiff = x1[n] - x2[n]
    hDiff = y1[n] - y2[n]
    while wDiff <= 1 and wDiff >= -1:
        x1[n]+=1
        x2[n]-=1
        wDiff = x1[n] - x2[n]
    while hDiff <= 1 and hDiff >= -1:
        y1[n]+=1
        y2[n]-=1
        hDiff = y1[n] - y2[n]

    x1[n] = x1[n]*wMultiplier-w*0.1
    x2[n] = x2[n]*wMultiplier-w*0.1
    y1[n] = y1[n]*hMultiplier-h*0.1
    y2[n] = y2[n]*hMultiplier-h*0.1
    
  #print("X1:",x1," X2:", x2, " Y1:", y1, " Y2:", y2)

  # Generate 10 unique random shapes
  s = set()
  
  for i in range(len(x1)):
    s.add((x1[i], y1[i], x2[i], y2[i]))

  #print("Shape:",shapes)
  return s

def generateBarcodeImage(sn):
  #Needs to be generated during the serial number generation before the first bit gets discarded
  #Use firt digit to define shape type
  shapeType = sn[0] #steals the first bit before it gets discarded
  shapeType = int(shapeType, 16) % 3

  #if verifying a code it should already be formatted
  #need to apply the same hashing to the serial number so it has the correct checksum 
  sn=sn[1:]
  # Compute the SHA-256 hash of the serial number
  hash = hashlib.sha256(sn.encode()).hexdigest()
  # Use the last digit of the hash as the checksum
  checksum = hash[-1]
  #add the checksum to the sn
  sn += checksum

  # defines the desired dimensions
  width = 300
  height = 100

  shapes = convertSNtoCoordinates(sn, width, height)


  # Create a new image with the desired size and drawer object
  image = Image.new('RGBA', (width, height), (0,0,0,0))
  drawer = ImageDraw.Draw(image)

  drawer.rectangle((0,0,width,height), outline="black", fill=None, width=2)
  font = ImageFont.truetype("fonts/Helvetica.ttf", 26)
  #drawer.text((65, 65), sn.upper(), (65,65,65), font=font, align="right")
  #didn't like text obscuring image

  if shapeType == 0:
    # Generate circle barcode image
    #print("Shape: Circle")
    for circle in shapes:
        drawer.ellipse(circle, outline="black", fill=None, width=2)
        
  if shapeType == 1:
    # Generate line barcode image
    #print("Shape: Line")
    for line in shapes:
        drawer.line(line, fill="black", width=2)

  if shapeType == 2:
    # Generate square barcode image
    #print("Shape: Rectangle")
    for rectangle in shapes:
        drawer.rectangle(rectangle, outline="black", fill=None, width=2)
   
  # Return the generated image
  return image

def generateSerial():
    #Should include an environmental variable for true randomness
    #generate the random hex serial number
    sn=secrets.token_hex(6) 
    #generate barcode before discarding first bit used as shape definer
    barcode.append(generateBarcodeImage(sn))

    #remove a digit to make the sn length 11 before adding the checksum
    sn=sn[1:]
    # Compute the SHA-256 hash of the serial number
    hash = hashlib.sha256(sn.encode()).hexdigest()
    # Use the last digit of the hash as the checksum
    checksum = hash[-1]
    #add the checksum to the sn
    sn += checksum

    return sn

def getWIF(pk_hex):
    # PK0 is the private key hex
    PK0 = pk_hex
    PK1 = '80'+ PK0
    PK2 = hashlib.sha256(codecs.decode(PK1, 'hex'))
    PK3 = hashlib.sha256(PK2.digest())
    checksum = codecs.encode(PK3.digest(), 'hex')[0:8]
    PK4 = PK1 + str(checksum)[2:10]  #I know it looks wierd

    WIF = base58.b58encode(binascii.unhexlify(PK4))
    
    return WIF

def generateQR(text, private=True):
    # Create a QR code object
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
    )

    # Set the text to encode in the QR code
    qr.add_data(text)
    qr.make(fit=True)

    # Generate the private QR code image
    if (private):
        return qr.make_image(fill_color=(96, 96, 96), back_color=(128,128,128))
    else:    
        return qr.make_image()
    
def replaceTemplateData(template, blockchain, pub_keys, pub_adds, pub_qrs, priv_keys, wifs, priv_qrs, sns, sec_imgs):
    try:
        assert blockchain == "Bitcoin"
    except AssertionError:
        return "Error: Bitcoin is currently the only supported blockchain"

    # Open the HTML file in read-only mode
    with open(template, "r") as f:
      # Read the contents of the file
      html = f.read()
      fileName = template.split("/")
      fileName = fileName[len(fileName)-1]
      print(fileName)

    date = datetime.datetime.now().strftime("%m/%d/%Y")
    html = html.replace("{{Date}}", date)
    html = html.replace("{{Blockchain}}", blockchain)

    # Loop through the elements in the `pub_keys` array
    for i, (pub_key, pub_add, pub_qr, priv_key, wif, priv_qr, sn, sec_img)  in enumerate(zip(pub_keys, pub_adds, pub_qrs, priv_keys, wifs, priv_qrs, sns, sec_imgs)):
      # Build the placeholder string using string concatenation
      pub_key_ph = "{{PubKey" + str(i) + "}}"
      pub_add_ph = "{{PubAddress" + str(i) + "}}"
      pub_qr_ph = "{{PubQR" + str(i) + "}}"
      priv_key_ph = "{{PrivKey" + str(i) + "}}"
      wif_ph = "{{WIF" + str(i) + "}}"
      priv_qr_ph = "{{PrivQR" + str(i) + "}}"
      sn_ph = "{{SerialN" + str(i) + "}}"
      sec_img_ph = "{{SecImage" + str(i) + "}}"
      low_sec_img_ph = "{{LowSecImage" + str(i) + "}}"
      
      pub_qr_buff = io.BytesIO()
      priv_qr_buff = io.BytesIO()
      sec_img_buff = io.BytesIO()
      low_sec_img_buff = io.BytesIO()
      pub_qr.save(pub_qr_buff, format="PNG")
      priv_qr.save(priv_qr_buff, format="PNG")
      sec_img.save(sec_img_buff, format="PNG")
      low_sec_img=sec_img.resize((150,50))
      low_sec_img.save(low_sec_img_buff, format="PNG")

      # Encode the image data as a base64 string
      pub_qr_str = base64.b64encode(pub_qr_buff.getvalue()).decode()
      priv_qr_str = base64.b64encode(priv_qr_buff.getvalue()).decode()
      sec_img_str = base64.b64encode(sec_img_buff.getvalue()).decode()
      low_sec_img_str = base64.b64encode(low_sec_img_buff.getvalue()).decode()

      # Create an HTML image tag using the base64 encoded string
      pub_qr_html = f'<img src="data:image/png;base64,{pub_qr_str}" width=300 height=300 alt="Public Address">'
      priv_qr_html = f'<img src="data:image/png;base64,{priv_qr_str}" width=300 height=300 alt="Wallet Import Format (WIF) Address">'
      sec_img_html = f'<img src="data:image/png;base64,{sec_img_str}" width=300 height=100 alt="Security Barcode">'
      low_sec_img_html = f'<img src="data:image/png;base64,{low_sec_img_str}" width=300 height=100 alt="Security Barcode - Low Resolution">'

      # Replace the placeholder with the value of the `public_key` variable
      html = html.replace(pub_key_ph, pub_key)
      html = html.replace(pub_add_ph, pub_add)
      html = html.replace(pub_qr_ph, pub_qr_html)
      html = html.replace(priv_key_ph, priv_key)
      html = html.replace(wif_ph, wif.decode())
      html = html.replace(priv_qr_ph, priv_qr_html)
      html = html.replace(sn_ph, sn.upper())
      html = html.replace(sec_img_ph, sec_img_html)
      html = html.replace(low_sec_img_ph, low_sec_img_html)

    # Write the updated HTML to a new file
    with open("output/Sheet-"+fileName, "w") as f:
      f.write(html)

    #Wallet Builder
    
    return True

#Generate 10 new scratch wallets (10 cards print per page) define arrays
walletsPerPage = 10
wallets = set()
privKey = []
pubKey = []
wif = []
pubAddress = []
pubQR = []
privQR = []
serial = []

while len(wallets) < walletsPerPage:
    blockchain = "Bitcoin"
    #Generate a new seed phrase, to be used in v2
    seedPhrase = Mnemonic().generate()

    #Generate private and public keys
    privKey.append(ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1))
    pubKey.append(privKey[len(wallets)].get_verifying_key())

    #convert to hex for logic
    privKey[len(wallets)] = privKey[len(wallets)].to_string().hex()
    pubKey[len(wallets)] = pubKey[len(wallets)].to_string().hex()

    #Create base58 encoded addresses
    wif.append(getWIF(privKey[len(wallets)])) 
    pubAddress.append(bitcoin.privkey_to_address(privKey[len(wallets)])) #gotta check to make sure this library doesn't transmit or otherwise compromise a private key.

    #create QR codes for public and private address/WIF
    pubQR.append(generateQR(pubAddress[len(wallets)], False))
    privQR.append(generateQR(wif[len(wallets)])) #must make sure this library doesn't transmit sensitive information
    #Generate a unique serial number
    serial.append(generateSerial())
    
    

    wallets.add("SUCCESS: Wallet"+str(len(wallets)))
#barcode[0].show()
print(wallets)
replaceTemplateData("templates/Avery5371Public.html", blockchain, pubKey, pubAddress, pubQR, privKey, wif, privQR, serial, barcode)
replaceTemplateData("templates/Avery5371Private.html", blockchain, pubKey, pubAddress, pubQR, privKey, wif, privQR, serial, barcode)

