import rospy
from std_msgs.msg import String
import sys
from wifi_sensor.msg import *
import time


l1=[];
sec=time.time()
msg = Rssi()

def callback(data):
	rssi1=data.rssi
	mac1=data.their_mac_addr
	#print mac1
	#print rssi1
	if not mac1 in l1:
		l1.append(mac1)
	#print "Acces"


def callback2(data):
	rssi=data.rssi
	mac=data.their_mac_addr
	#print mac
	#print rssi
	pub(mac,rssi)

def pub(mac,rssi):
	sec2=time.time()
	if (sec2 - sec) > 15:
		print(l1) 
		if not mac in l1:
			#print mac
			#print rssi 
			msg.header.stamp = rospy.Time.now()
		        msg.my_mac_addr = ""
		        msg.their_mac_addr = mac
		        msg.rssi = rssi
			
		    				

def listener():
	rospy.init_node('listener_acces_{0}'.format(sys.argv[1]), anonymous=True)	
	rospy.Subscriber("/rssi_acces_{0}".format(sys.argv[1]), Rssi, callback)
	print "rssi_acces_{0}".format(sys.argv[1])
	rospy.Subscriber("/rssi_all_{0}".format(sys.argv[1]), Rssi, callback2)
	pub = rospy.Publisher("rssi_clients_{0}".format(sys.argv[1]),Rssi,queue_size=10)	
	r = rospy.Rate(10)
	while not rospy.is_shutdown():
	      secs=time.time()
	      if (secs - sec) > 15: 
		      #rospy.loginfo(msg)
	 	      pub.publish(msg)
	  	      r.sleep()


	
		
