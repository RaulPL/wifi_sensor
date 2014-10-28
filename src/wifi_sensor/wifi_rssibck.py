#!/usr/bin/env python

import rospy
import time
import numpy as np
from wifi_sensor.msg import *
import thread
import subprocess
import sys



class WifiSensor():
    def __init__(self):
        rospy.init_node("wifisensor")
        self.rate = rospy.get_param("~rate", 30)
        self.my_addr = "e8:03:9a:84:80:ed"
        self.data = {}
        self.dataMutex = thread.allocate_lock()
        thread.start_new_thread(self.mesRaw, ())
        self.pub = rospy.Publisher("rssi_{0}".format(sys.argv[2]),
                                   Rssi,
                                   queue_size=10)
        r = rospy.Rate(self.rate)
        while not rospy.is_shutdown():
            data = {}
            with self.dataMutex:
                data = dict(self.data)
                self.data = {}
            msg = Rssi()
            for addr in data.keys():
                #submsg = Rssi()
                msg.header.stamp = rospy.Time.now()
                msg.my_mac_addr = self.my_addr
                msg.their_mac_addr = addr
                msg.rssi = data[addr]
                #msg.data.append(submsg)
            	self.pub.publish(msg)
            r.sleep()


    def mesRaw(self):
		if sys.argv[1] == "0":
			p = subprocess.Popen(
			    ("tcpdump", "-nnevvv","-s 0", "-i", "mon0", "(type mgt subtype probe-resp)", "or" ,"(type mgt subtype beacon)"),
			    stdout=subprocess.PIPE
			    )
		elif sys.argv[1] == "1":
			p = subprocess.Popen(
			    ("tcpdump", "-nnevvv","-s 0", "-i", "mon0", "(not type mgt subtype probe-resp)", "and" ,"(not type mgt subtype beacon)"),
			    stdout=subprocess.PIPE
			    )
		else:
			print "parametro no indicado 0- Acces Point 1- Cliente"
			thread.exit()
		while not rospy.is_shutdown():
			    try:
				for line in iter(p.stdout.readline, ""):
				    chunks = line.split(" ")
				    addr = None
				    rssi = None
				    if chunks[17] != "Probe":
				    	print chunks[0]#TimeStamp
				    	rssi= int(chunks[8][0:-2])#Potencia
				    	addr = chunks[13][6:]#Bssid
					print str(chunks[17][1:-1]) #Essid
				    else:
					print chunks[0] #TimeStamp
				    	rssi= int(chunks[8][0:-2])#Potencia
				    	addr = chunks[14][6:] #BSSid
					print chunks[19][1:-1]#Essid
				    if addr is not None and rssi is not None and rssi < 0:
		                		with self.dataMutex:
		                    			if addr in self.data.keys():
								self.data[addr]=[]
		                        			self.data[addr].append(rssi)
		                    			else:
		                   				self.data[addr] = [rssi]
			    except:
				pass

