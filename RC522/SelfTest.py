import RPi.GPIO as GPIO
import rc522Lib as rc
import signal
import time

continue_reading = True
write="Marwen"

rc.MFRC522_Init('/dev/spidev0.0', 1000000)
print "Welcome to the MFRC522 data write example"

i=0
while i<25:
    rc.Write_MFRC522(0x09, 0)
    i=i+1
rc.Write_MFRC522(0x01, 0x01)
#rc.Write_MFRC522(0x0A, 0x80) ##initiate the FIFOLevelReg pointer

rc.Write_MFRC522(0x36, 0x09)
rc.Write_MFRC522(0x0A, 0x80) ##initiate the FIFOLevelReg pointer
if rc.Read_MFRC522(0x05)==0x04:
    print "crc finished "
    rc.ClearBitMask(0x05, 0x04) #DivIrqReg

rc.Write_MFRC522(0x09, 0x00)

#rc.Write_MFRC522(0x03, 0x04)
rc.Write_MFRC522(0x01, 0x03) #enable CRC Command
i=0xff
while i<0:
    n=Read_MFRC522(0x05)
    i=i-1
    if(i==0 or n&0x04):
        break
print "crc MSB: ",rc.Read_MFRC522(0x21) #CRCResultRegM
print "crc LSB: ",rc.Read_MFRC522(0x22)
print "Error Reg: ",rc.Read_MFRC522(0x06)

print "{0:x}".format(rc.Read_MFRC522(0x09))
print "{0:x}".format(rc.Read_MFRC522(0x09))
print "{0:x}".format(rc.Read_MFRC522(0x09))
print "{0:x}".format(rc.Read_MFRC522(0x09))
