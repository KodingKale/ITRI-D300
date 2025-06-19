class SerialPackets:
    header = b'\00\00'
    def __innit__(self, data):
        self.data = data

    def construct(self):
        return(self.header + self.data + self.checksum(self.header + self.data))    

    def checksum(self):
        MSB = 0
        LSB = 0
        for byte in self.data:
            MSB = (MSB + byte) & 0xFF  # Ensure 8-bit result using & 0xFF
            LSB = (LSB + MSB) & 0xFF
        # Return the two checksum bytes
        return(bytes([MSB, LSB]))