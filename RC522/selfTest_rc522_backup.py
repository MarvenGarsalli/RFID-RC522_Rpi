import RPi.GPIO as GPIO
import rc522Lib as rc
import spi
import signal
import time

rc.MFRC522_Init('/dev/spidev0.0', 1000000)
#rc.Write_MFRC522(0x01, 0x10)# Power down mode: if ther is no SoftReset

##spi.openSPI('/dev/spidev0.0', 1000000)
##GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN)
GPIO.setup(8, GPIO.OUT)
GPIO.output(8, 0) #NRSTPD

print "Welcome to the MFRC522 self test example"
rc.Write_MFRC522(0x2A, 0x14) #TModeReg :2^10 + autorestart # was 0x14
rc.Write_MFRC522(0x2B, 0x00) #TPrescalerReg
rc.Write_MFRC522(0x2C, 0xFF) #reload value: 65535
rc.Write_MFRC522(0x2D, 0xFe)

#rc.Write_MFRC522(0x04, 0x81) #ComIrqReg
##rc.Write_MFRC522(0x02, 0x04) #ComIEnReg: Activate interrupt signal pin IRQ
rc.Write_MFRC522(0x0C, 0x40) #ControlReg: timer starts immediately
#=> wait 4.8329 sec
#rc.Write_MFRC522(0x01, 0x01)#*_* stores 25 bytes from the FIFO to the internal buffer
rc.Write_MFRC522(0x11, 0x20) #transmitter can only be started if an RF field is generated
print "{0:x}".format(rc.Read_MFRC522(0x14))
rc.Write_MFRC522(0x14, 0x83)
rc.Write_MFRC522(0x02, 00)
def sendrequest():
    rc.ClearBitMask(0x04, 0x80) #CommIrqReg
    rc.Write_MFRC522(0x02, 0xA2)#ComIEnReg, Enable err, timeout and receive interrupt
    buf=[]
    buf.append(0x26)
    rc.Write_MFRC522(0x0D, 0x07)
    # bout=rc.CalulateCRC(buf)#Calc CRC
    # buf.append(bout[0])
    # buf.append(bout[1])
    rc.Write_MFRC522(0xA0, 0x80)
    rc.Write_MFRC522(0x09, buf[0])

    rc.Write_MFRC522(0x01, 0xC0)
    rc.Write_MFRC522(0x0D, 0x80)
    i=0xff
    while True:
        n=rc.Read_MFRC522(0x04)
        i=i-1
        if(i==0 or n&0x30):
            if(i != 0):
                print "card detected!!"
            break;
    rc.Write_MFRC522(0x01, 0x00)
    rc.ClearBitMask(0x0D, 0x80)
    #rc.Write_MFRC522(0x13, 0x00)#RxModeReg: receiver is deactivated after receiving a data frame

while True:
    if(GPIO.input(7)==True):
        GPIO.output(8, 1)
        #print "{0:x}:{0:x}".format(rc.Read_MFRC522(0x2E), rc.Read_MFRC522(0x2F)) #TCounterValReg : the current value of the timer
    #time.sleep(0.4)
    GPIO.output(8, 0)
    sendrequest()

#spi.transfer(((0x0A<<1)&0x7E, 0x80)) #initiate the FIFOLevelReg pointer

# i=10
# while (i<25):
#     spi.transfer(((0x09<<1)&0x7E, i))
#     i=i+1
# while(1):
#     time.sleep(1)
#     print spi.transfer(((0x09<<1)|0x80,0))[1]

#print "{0:x}".format(spi.transfer(((0x09<<1)|0x80,0)))
