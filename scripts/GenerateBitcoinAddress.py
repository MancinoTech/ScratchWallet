import ecdsa
import qrcode
import codecs  #If not installed: "pip3 install codecs"
import hashlib
import base58
import bitcoin
import binascii
from PIL import Image, ImageEnhance

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

    # Generate the public QR code image
    if (private):
        return qr.make_image(fill_color=(69, 69, 69), back_color=(96, 96, 96))
    else:    
        return qr.make_image()
    

def compressPubKey(pk_hex):
    #PA0 is the public key hex, PA4 is the public address
    PA0 = pk_hex
    PA1 = '04'+ PA0 #bitcoin prefix
    # Checking if the last byte is odd or even
    if (ord(bytearray.fromhex(PA1[-2:])) % 2 == 0):
        PA2 = '02' + PA1[2:66]
    else:
        PA2 = '03' + PA1[2:66]

    # Add bytes 0x02 to the X of the key if even or 0x03 if odd
    return PA2

def checkKeys(pub, pri):

    # Convert the private key from hexadecimal to binary format
    private_key = codecs.decode(pri, 'hex')

    # Create an ECDSA signing key using the private key
    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)

    # Define the message to sign
    message = "Hello, world!"

    # Sign the message with the private key
    signature = sk.sign(message.encode('utf-8'))

    # Convert the signature to hexadecimal format
    #signature_hex = codecs.encode(signature, 'hex')

    # Convert the public key from hexadecimal to binary format
    public_key = codecs.decode(pub, 'hex')

    # Create an ECDSA verifying key using the public key
    vk = ecdsa.VerifyingKey.from_string(public_key, curve=ecdsa.SECP256k1)

    # Verify the signature using the public key
    if vk.verify(signature, message.encode('utf-8')):
        print("The private and public key pair is correct.")
    else:
        print("The private and public key pair is incorrect.")


# Generate a new private key using the ECDSA algorithm
sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)

# Derive the corresponding public key
vk = sk.get_verifying_key()

# Encode the private key and public key in hexadecimal format
private_key = sk.to_string()
private_key_hex = private_key.hex()
public_key = vk.to_string()
public_key_hex = public_key.hex()

wif = getWIF(private_key_hex)
pubKey = bitcoin.privkey_to_pubkey(private_key_hex)
compPubKey = compressPubKey(pubKey)
pubAddress = bitcoin.privkey_to_address(private_key_hex)

# Display the private and public keys
#print("Private key:", private_key_hex)
#print("WIF:", wif.decode())
#print("Public key:", pubKey)
#print("Compressed Public key:", compPubKey)
#print("Public Address:", pubAddress)

pubQR = generateQR(pubAddress, 0)
pubQR.save("pubQR.png")
img = Image.open("pubQR.png")
img.show()

privQR = generateQR(wif, 1)
privQR.save("privQR.png")
img = Image.open("privQR.png")
img.show()

checkKeys(public_key_hex, private_key_hex)


