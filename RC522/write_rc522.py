#import RPi.GPIO as GPIO
import rc522Lib as rc
import signal
import time

continue_reading = True
write="Hello World!"
# Fill the data with 0xFF
data=[]
for l in write:
    data.append(ord(l))
for x in range(len(write),16):
    data.append(0xF0)

rc.MFRC522_Init('/dev/spidev0.0', 1000000)
print "Welcome to the MFRC522 data write example"

print rc.Read_MFRC522(0x01) #==0x0F :reset

while continue_reading:
    # Scan for cards
    (status,TagType) = rc.MFRC522_Request(0x26) #PICC_REQIDL
    # If a card is found
    if status == 0: #MI_OK
        print "Card detected"
    # Get the UID of the card
    (status,uid) = rc.MFRC522_Anticoll()
    #print("uid: ",uid)
    # If we have the UID, continue
    if status == 0:
        print "Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3])
        # This is the default key for authentication
        key = [0xA0,0xA1,0xA2,0xA3,0xA4,0xA5]
        key0= [0x00,0x00,0x00,0x00,0x00,0x00] #from this key
        key1= [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF] #to this: 2^48=2.7*10^14
        # Select the scanned tag
        rc.MFRC522_SelectTag(uid)
        # Authenticate
        status = rc.MFRC522_Auth(0x60, 8, key1, uid) #PICC_AUTHENT1A
        # Check if authenticated
        if status == 0:
            print "Initially: "
            rc.MFRC522_Read(8)
            rc.MFRC522_Write(8,data)
            print "After writing: "
            backData=rc.MFRC522_Read(8)
            if len(backData) == 16:
                CardData=""
                for elt in backData:
                    if ord(chr(elt).upper())> 64 and ord(chr(elt).upper())<91:
                        CardData += chr(elt)
                print "Data: ",CardData
            rc.MFRC522_StopCrypto1()
            continue_reading=False
        else:
            print "Authentication error"
            continue_reading=False
GPIO.cleanup()
