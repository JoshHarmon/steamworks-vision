 
#from networktables import NetworkTables
#import time

#default = False
#connected = False

#table = None


#while True:
	#NetworkTables.initialize(server="10.28.11.30")
	#if NetworkTables.isConnected():
		#print("yay!")
		
		#table = NetworkTables.getTable("VisionTest")
		
		#if(table):
			#table.putBoolean("Success",True)
	#else:
		#print("nay!")




#def NT_initialize(address):
	#try:
		#NetworkTables.initialize(server=address)
		#print("Connected to ", address)
		#NT_getTable()
		#return True
	#except:
		#return False
	#else:
		#return False

#def NT_getTable(tableName="vision"):
	#if NetworkTables.isConnected():
		#table = NetworkTables.getTable(tableName)
		#print("Network table located!")
		#return table
	#else:
		#return None
	
#def NT_putBoolean(key,value):
	#try: return table.putBoolean(key,value)
	#except: return default
	
#NetworkTables.initialize("10.28.11.30")


#if NetworkTables.isConnected():
	#table = NetworkTables.getTable(tableName)
	
	#if not table == None:
		#print("Network table located! Setting test value...")
		#table.putBoolean("test", True)
	#else:
		#print("Table == none")
#else:
		#print("Not connected")
	
#time.sleep(10)


import sys
import time
from networktables import NetworkTables

# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) != 2:
    print("Error: specify an IP to connect to!")
    exit(0)

ip = sys.argv[1]

NetworkTables.initialize(server="roboRIO-2811-FRC.local")
visionTable = NetworkTables.getTable("vision")

visionTable.putBoolean("vision", True)

i = 0
while True:
    try:
        print('robotTime:', visionTable.getNumber('robotTime'))
    except KeyError:
        print('robotTime: N/A')

    visionTable.putNumber('dsTime', i)
    time.sleep(1)
    i += 1
