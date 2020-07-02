import os
import sys
import struct
from decimal import Decimal

# Open the log file
with open(sys.argv[1], 'rb') as f:

	# Read it completely
	buf = f.read()

	# Convert endianness
	buf = struct.unpack('<'+str(len(buf))+'s', buf)[0]

	# Iterate over the data
	i = 0
	while i < len(buf):

		# Read one float sized chunk
		chunk = buf[i:i+8]

		while len(chunk) < 8:
			chunk += "\0"

		# Unpack the chunk to a 64-bit integer
		flt = struct.unpack('q', chunk)[0] & 0xffffffffffffffff # Make sure its unsigned

		# Print out the integer as a float
		print(float("{:.2f}".format(flt)))

		# Move over to the next float sized chunk
		i+=8
