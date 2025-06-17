def fletcher_checksum(data):
    '''
    Calculate Fletcher checksum for 3DM-CV7-INS
    data: bytes object containing the message to checksum
    Returns: 2 bytes checksum
    '''
    MSB = 0
    LSB = 0
    for byte in data:
        MSB = (MSB + byte) & 0xFF  # Ensure 8-bit result using & 0xFF
        LSB = (LSB + MSB) & 0xFF
    # Return the two checksum bytes
    return(bytes([MSB, LSB])) 

print(fletcher_checksum(bytes([0x75, 0x65, 0x0C, 0x0B, 0x0B, 0x0F, 0x01, 0x80, 0x02, 0xD3, 0x00, 0x01, 0x04, 0x00, 0x01])).hex())
