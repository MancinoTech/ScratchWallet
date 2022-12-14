#Barcode verifyer
import hashlib
import numpy
from PIL import Image, ImageDraw

def convertSNtoCoordinates(sn, w, h):
      #extend the serial number to build more shapes
  hash = hashlib.sha256(sn.encode()).hexdigest()
  seed = [int(c, 16) for c in hash]

  # Split the array into 4 equal arrays
  x1 = numpy.array_split(seed, 4)[0]
  x2 = numpy.array_split(seed, 4)[1]
  y1 = numpy.array_split(seed, 4)[2]
  y2 = numpy.array_split(seed, 4)[3]

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

#Require serial number
def verifyBarcodeImage(sn):

  # Define the desired size
  width = 150
  height = 50

  shapes=convertSNtoCoordinates(sn, width, height)

  # Create a drawer object for drawing on the image
  image = Image.new('RGB', (width, height), (255, 255, 255))
  drawer = ImageDraw.Draw(image)
  #Variable to hold all 3 results
  verifier = []

  # Generate circle barcode image
  for circle in shapes:
      drawer.ellipse(circle, outline="black", fill=None, width=2)
  verifier.append(image)

  #reset the image and drawer
  image = Image.new('RGB', (width, height), (255, 255, 255))
  drawer = ImageDraw.Draw(image)

  # Generate line barcode image
  for line in shapes:
      drawer.line(line, fill="black", width=2)
  verifier.append(image)
  
  #reset the image and drawer
  image = Image.new('RGB', (width, height), (255, 255, 255))
  drawer = ImageDraw.Draw(image)

  # Generate square barcode image
  for rectangle in shapes:
      drawer.rectangle(rectangle, outline="black", fill=None, width=2)
  verifier.append(image)

  #reset the image and drawer
  image = Image.new('RGB', (width, height), (255, 255, 255))
  drawer = ImageDraw.Draw(image)

  # Return the generated images
  return verifier

#verifying mode by passing a true value
images = verifyBarcodeImage("c9b7c1ee48ef")

for i in range(len(images)):
    images[i].show()