# This code is adapted from Safiqul's header.py code: https://github.com/safiqul/2410/blob/main/header/header.py

from struct import *

# Header format for packets: 4 unsigned short integers (each 2 bytes) = 8 bytes total
header_format = 'HHHH'

"""Variables for flags using bit positions"""
SYN = (1 << 3)  # Set bit 3 (0b1000)
ACK = (1 << 2)  # Set bit 2 (0b0100)
FIN = (1 << 1)  # Set bit 1 (0b0010)

"""Description: Creates a packet consisting of header and data (payload)
Arguments: sequence number(int), acknowledgement(int), flags(int), window size(int), data (bytes)
Returns: A bytes object with the packed header and data, or None if there is an error packing the header."""
def create_packet(seq, ack, flags, win, data):
    try:
        return pack(header_format, seq, ack, flags, win) + data
    except (TypeError, error) as e: # If datatypes are wrong or other error
        print(f"There was an error creating the header: {e}")
        return None # Exit if error

"""Description: Unpacks the header in the defined format.
Argument: A byte string of 8 bytes (2 bytes per field).
Returns a tuple (seq, ack, flags, win) with the unpacked values, or None if unpacking fails."""
def parse_header(header):
    try:
        return unpack(header_format, header)
    except (TypeError, error) as e:
        print(f"There was an error parsing header: {e}")
        return None

"""Function for decoding the flags from a bitfield, using bitwise operations.
Arguments: Integer where bits represent flags: bit 3 = SYN, bit 2 = ACK, bit 1 = FIN
Returns a tuple of integers that indicates whether a flag is set (non-zero) or not (zero)"""
def parse_flags(flags):
    return (
        flags & SYN,
        flags & ACK,
        flags & FIN
    )



