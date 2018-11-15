
import RPi.GPIO as GPIO
import rc522Lib as rc
import signal
import time

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False

signal.signal(signal.SIGINT, end_read) # Hook the SIGINT
rc.MFRC522_Init('/dev/spidev0.0', 1000000)
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
print rc.Read_MFRC522(0x01) #==0x0F :reset
rc.Write_MFRC522(0x01, 0x10)
#rc.Write_MFRC522(0x11,0x20)
while continue_reading:
    # Scan for cards
    (status,TagType) = rc.MFRC522_Request(0x26) #PICC_REQIDL
    # If a card is found
    if status == 0: #MI_OK
        print "Card detected"
    # Get the UID of the card
    (status,uid) = rc.MFRC522_Anticoll()
    #print("(uid, status): ",uid,"\t ", status)
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
            rc.MFRC522_Read(8)
            rc.MFRC522_StopCrypto1()
            continue_reading=False
        else:
            print "Authentication error"
            ###rc.MFRC522_Reset() :stop everything
            # (s,TagType) = rc.MFRC522_Request(0x26)
            # (s,uid) = rc.MFRC522_Anticoll()
            # rc.MFRC522_SelectTag(uid)
            # s=rc.MFRC522_Auth(0x60, 8, key, uid) #PICC_AUTHENT1A
            # if s == 0:
            #     rc.MFRC522_Write("50")
            #     rc.MFRC522_StopCrypto1()
            continue_reading=False
GPIO.cleanup()
