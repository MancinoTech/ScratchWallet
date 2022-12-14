import bitcoinlib

# Create a new transaction object
tx = bitcoinlib.Transaction()

# Set the transaction fee (in satoshis per byte)
fee_rate = bitcoinlib.estimate_fee_rate()
tx.fee_rate = fee_rate

# Set the recipient's address to the null address
tx.add_output(bitcoinlib.Address(b'\x00' * 20), 0)

# Include the serial number in the scriptSig field
serial_number = '...'  # Replace with the actual serial number
tx.add_input(b'', 0, script_sig=serial_number)

# Sign the transaction with your private key
tx.sign(my_private_key)

# Broadcast the transaction to the network
tx.broadcast()

######################################################################

import hashlib

# Get the serial number from the card
serial_number = '...'  # Replace with the actual serial number from the card

# Hash the serial number using SHA-256
hash_function = hashlib.sha256()
hash_function.update(serial_number.encode('utf-8'))
hashed_serial_number = hash_function.hexdigest()

# The hashed serial number can be added to the blockchain without making the original value publicly readable

#User will enter Public Address and SN, SN will get hashed and compared to the hashed SN in the wallet creation transaction. If the wallet contains a transaction with the correct hashed SN and the transaction came from a wallet owned by the wallet/script creator return a value of authenticity.