import RPi.GPIO as GPIO
import spi
import signal
import time


def Write_MFRC522( addr, val):
  spi.transfer(((addr<<1)&0x7E,val))

def MFRC522_Reset():
  Write_MFRC522(0x0A, 0x80) #immediately clears the internal FIFO buffer s read and write pointer and ErrorReg register s BufferOvfl bit
  Write_MFRC522(0x01, 0x0F)  #CommandReg, SoftReset

def Read_MFRC522( addr):
  val = spi.transfer((((addr<<1)&0x7E) | 0x80,0))
  return val[1]

def SetBitMask( reg, mask):
  tmp = Read_MFRC522(reg)
  Write_MFRC522(reg, tmp | mask)

def ClearBitMask( reg, mask):
  tmp = Read_MFRC522(reg);
  Write_MFRC522(reg, tmp & (~mask))

def AntennaOn():
  temp = Read_MFRC522(0x14)#TxControlReg
  print "AntennaOn()::temp= {0:x}".format(temp)
  if(~(temp & 0x03)):
    SetBitMask(0x14, 0x03)

def AntennaOff():
  ClearBitMask(0x14, 0x03) #TxControlReg

def MFRC522_StopCrypto1():
  ClearBitMask(0x08, 0x08) #Status2Reg

def MFRC522_ToCard(command, sendData):
    backData = []
    backLen = 0
    status = 2
    irqEn = 0x00
    waitIRq = 0x00
    lastBits = None
    n = 0
    i = 0

    if command == 0x0E : #PCD_AUTHENT:
      irqEn = 0x12
      waitIRq = 0x10
    if command == 0x0C : #PCD_TRANSCEIVE:
      irqEn = 0x77
      waitIRq = 0x30

    Write_MFRC522(0x02, irqEn|0x80) #CommIEnReg
    ClearBitMask(0x04, 0x80) #CommIrqReg
    SetBitMask(0x0A, 0x80) #FIFOLevelReg
    Write_MFRC522(0x01, 0x00); #PCD_IDLE: cancel current command execution
    while(i<len(sendData)):
      Write_MFRC522(0x09, sendData[i]) #FIFODataReg
      i = i+1
    Write_MFRC522(0x01, command) #CommandReg
    if command == 0x0C: #PCD_TRANSCEIVE
      SetBitMask(0x0D, 0x80) #BitFramingReg: start sending

    i = 2000
    while True:
      n = Read_MFRC522(0x04)
      i = i - 1
      if ~((i!=0) and ~(n&0x01) and ~(n&waitIRq)):  #and ~(n&0x60)
        break
    ClearBitMask(0x0D, 0x80)
    if i != 0:
      if (Read_MFRC522(0x06) & 0x1B)==0x00: #ErrorReg
        status = 0
        if n & irqEn & 0x01: #if n==1,3,5,7,9,b,d,f: timeout occur
          print "check*******************"
          status = 1
        if command == 0x0C: # PCD_TRANSCEIVE
          n = Read_MFRC522(0x0A) #FIFOLevelReg
          lastBits = Read_MFRC522(0x0C) & 0x07 #Read ControlReg
          if lastBits != 0:
            backLen = (n-1)*8 + lastBits
          else:
            backLen = n*8
          if n == 0:
            n = 1
          if n > 16:
            n = 16
          i = 0
          while i<n:
            backData.append(Read_MFRC522(0x09))#FIFODataReg
            i = i + 1;
      else:
        status = 2
    return (status,backData,backLen)

def MFRC522_Request( reqMode):
    status = None
    backBits = None
    TagType = []
    Write_MFRC522(0x0D, 0x07)
    TagType.append(reqMode);
    (status,backData,backBits) = MFRC522_ToCard(0x0C, TagType) # PCD_TRANSCEIVE
    if ((status != 0) | (backBits != 0x10)):
      status = 2
    return (status,backBits)

def MFRC522_Anticoll():
  backData = []
  serNumCheck = 0
  serNum = []
  Write_MFRC522(0x0D, 0x00) #BitFramingReg
  serNum.append(0x93) #PICC_ANTICOLL
  serNum.append(0x20)
  (status,backData,backBits) = MFRC522_ToCard(0x0C,serNum) #PCD_TRANSCEIVE
  if(status == 0): #MI_OK
    i = 0
    if len(backData)==5:
      while i<4:
        serNumCheck = serNumCheck ^ backData[i]
        i = i + 1
      if serNumCheck != backData[i]:
        status = 2 #MI_ERR
    else:
      status = 2 #MI_ERR

  return (status,backData)

def CalulateCRC(pIndata):
  ClearBitMask(0x05, 0x04) #DivIrqReg
  SetBitMask(0x0A, 0x80); #FIFOLevelReg
  i = 0
  while i<len(pIndata):
    Write_MFRC522(0x09, pIndata[i])
    i = i + 1
  Write_MFRC522(0x01, 0x03) #CommandReg, PCD_CALCCRC
  i = 0xFF
  while True:
    n = Read_MFRC522(0x05)
    i = i - 1
    if not ((i != 0) and not (n&0x04)):
      break
  pOutData = []
  pOutData.append(Read_MFRC522(0x22)) #CRCResultRegL
  pOutData.append(Read_MFRC522(0x21)) #CRCResultRegM
  return pOutData

def MFRC522_SelectTag( serNum):
    backData = []
    buf = []
    buf.append(0x93) #PICC_SElECTTAG
    buf.append(0x70)
    i = 0
    while i<5:
      if i<len(serNum):
          buf.append(serNum[i])
      i = i + 1
    pOut = CalulateCRC(buf)
    buf.append(pOut[0])
    buf.append(pOut[1])
    (status, backData, backLen) = MFRC522_ToCard(0x0C, buf) #PCD_TRANSCEIVE
    if (status == 0) and (backLen == 0x18):
      print "Size: " + str(backData[0])
      return backData[0]
    else:
      return 0

def MFRC522_Auth( authMode, BlockAddr, Sectorkey, serNum):
    buff = []
    # First byte should be the authMode (A or B)
    buff.append(authMode)
    # Second byte is the trailerBlock (usually 7)
    buff.append(BlockAddr)
    # Now we need to append the authKey which usually is 6 bytes of 0xFF
    i = 0
    while(i < len(Sectorkey)):
      buff.append(Sectorkey[i])
      i = i + 1
    i = 0
    # Next we append the first 4 bytes of the UID
    while(i < 4):
      if i<len(serNum):
         buff.append(serNum[i])
      i = i +1
    # Now we start the authentication itself
    (status, backData, backLen) = MFRC522_ToCard(0x0E, buff) #PCD_AUTHENT
    # Check if an error occurred
    if not(status == 0):
      print "AUTH ERROR!!"
      return 2
    if not (Read_MFRC522(0x08) & 0x08) != 0: #Status2Reg
      print "AUTH ERROR(status2reg & 0x08) != 0"
    # Return the status
    return status

def MFRC522_Read( blockAddr): #blockAddr==8
    recvData = []
    recvData.append(0x30) #PICC_READ
    recvData.append(blockAddr)
    pOut = CalulateCRC(recvData)
    recvData.append(pOut[0])
    recvData.append(pOut[1])
    (status, backData, backLen) = MFRC522_ToCard(0x0C, recvData) #PCD_TRANSCEIVE
    if not(status == 0):
      print "Error while reading!"
    i = 0
    if backData != None and len(backData) == 16:
      print "Sector "+str(blockAddr)+" "+str(backData)
      return backData
def MFRC522_Write( blockAddr, data): #blockAddr==8
    recvData = []
    recvData.append(0xA0) #PICC_WRITE
    recvData.append(blockAddr)
    pOut = CalulateCRC(recvData)
    recvData.append(pOut[0])
    recvData.append(pOut[1])
    (status, backData, backLen) = MFRC522_ToCard(0x0C, recvData) #PCD_TRANSCEIVE
    if not(status == 0) or not(backLen == 4) or not((backData[0] & 0x0F) == 0x0A) :
        print "fuck me"
    buf=[]
    i=0
    while i<len(data):
        buf.append(data[i]) #ord() is #chr()
        i+=1

    pOut = CalulateCRC(buf)
    buf.append(pOut[0])
    buf.append(pOut[1])
    (status, backData, backLen) = MFRC522_ToCard(0x0C, buf) #PCD_TRANSCEIVE
    if not(status == 0) or not(backLen == 4) or not((backData[0] & 0x0F) == 0x0A):
      print "Error while writing!"
    i = 0
    if status==0:
      print "Writing successfully finished"

def MFRC522_Init1(dev, spd):
    spi.openSPI(device=dev,speed=spd)
    MFRC522_Reset();

def MFRC522_Init(dev, spd):
  spi.openSPI(device=dev,speed=spd)
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(22, GPIO.OUT)
  GPIO.output(22, 1) #NRSTPD

  MFRC522_Reset();
  # Write_MFRC522(0x2A, 0x8D) #TModeReg
  # Write_MFRC522(0x2B, 0x3E) #TPrescalerReg
  # Write_MFRC522(0x2D, 30) #TReloadRegL
  # Write_MFRC522(0x2C, 0) #TReloadRegH
  Write_MFRC522(0x15, 0x40) #TxAutoReg
  Write_MFRC522(0x11, 0x29) #ModeReg: or 0x3D #0xC9 MSBfirst will not work
  AntennaOn() # same as Write_MFRC522(0x14, 0x83)
