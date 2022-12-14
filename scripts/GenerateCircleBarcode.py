import random
from PIL import ImageDraw, Image

def generateBarcodeImage():
  # Create a new image with the desired size
  width = 300
  height = 100
  image = Image.new('RGB', (width, height), (255, 255, 255))

  # Create a drawer object for drawing on the image
  drawer = ImageDraw.Draw(image)

  # Generate 1000 unique random circles
  shapes = set()
  while len(shapes) < 9:
    x1 = random.randint(0-width*0.2, width-20)
    y1 = random.randint(0-height*0.2, height-20)
    x2 = random.randint(x1+20, width*1.2)
    y2 = random.randint(y1+20, height*1.2)
    shapes.add((x1, y1, x2, y2))

  # Draw the circles on the image
  for circle in shapes:
    drawer.ellipse(circle, outline="black", fill=None, width=2)
  # Return the generated image
  return image

# Generate a unique barcode image
barcodeImage = generateBarcodeImage()
barcodeImage.show()