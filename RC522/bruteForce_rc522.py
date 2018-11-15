
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
while continue_reading:
        # This is the default key for authentication
        key = [0xA0,0xA1,0xA2,0xA3,0xA4,0xA5]
        key0= [0x00,0x00,0x00,0x00,0x00,0x00] #from this key
        key1= [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF] #to this: 2^48=2.7*10^14
        keyx= [0xFA,0xFF,0xFF,0xFF,0xFF,0xFF]
        x=0xfffffffffffa

        status = 1
        while(status != 0):
            if status == 2: # Card not authenticated
                print "Wrong Key: ", keyx
                x=x+0b1
                #print "{0:b}".format(x)
                cpt=0
                while cpt<6:
                    keyx[cpt]= (int)(((x&(0xFF<<cpt*8))>>cpt*8))
                    cpt = cpt+1
            (st,TagType) = rc.MFRC522_Request(0x26)              # Scan for cards
            if st == 0:                                          # If a card is found
                (stat,uid) = rc.MFRC522_Anticoll()               # Get the UID of the card
                if stat == 0:                                    #if we have the UID, we continue
                    rc.MFRC522_SelectTag(uid)                    # Select the scanned tag
                    status = rc.MFRC522_Auth(0x60, 8, keyx, uid) # Authenticate
            #print keyx
            #raw_input("press any key")
        # Check if authenticated
        if status == 0:
            print "*_* Key: ", keyx, "*_*"
            rc.MFRC522_Read(8)
            rc.MFRC522_StopCrypto1()
        else:
            print "Authentication error"
            continue_reading=False
GPIO.cleanup()
