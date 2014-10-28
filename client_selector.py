import rospy
from std_msgs.msg import String

def callback(data):
	dat= rospy.loginfo(rospy.get_caller_id(),data.data)
	print dat


def listener():
	rospy.init_node('listener', anonymous=True)
	rospy.Subscriber("rssi_acces_{0}".format(sys.argv[1], String, callback) 
	rospy.spin()


if __name__ == '__main__':
	listener()
