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

NetworkTables.initialize(server=ip)
visionTable = NetworkTables.getTable("vision")

visionTable.putBoolean("vision_test", True)

i = 0
while True:
    try:
        visionTable.putNumber('vision_test_counter', i)
    except:
	print("Some error occurred when incrementing the vision test counter")
	
    time.sleep(1)
    i += 1
