import rospy
from wifi_sensor.msg import *
from geometry_msgs.msg import Twist
import collections
import numpy


class Controller(object):
    Target_addr = "f8:"
    max_len = 20
    vals_izq = collections.deque(maxlen=max_len)
    vals_der = collections.deque(maxlen=max_len)
    rospy.init_node("controller_pioneer")
    rospy.Subscriber("/rssi_acces_izq", Rssi, call_izq)
    rospy.Subscriber("/rssi_acces_der", Rssi, call_der)

    def __init__(self, lin_vel=0.4, ang_vel=0.2):
        pub = rospy.Publisher('/RosAria/cmd_vel', Twist, queue_size=10)
        max_lin = lin_vel
        max_ang = ang_vel
        thres = 5
        twist = Twist()
        twist.linear.y = 0
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        rate = rospy.Rate(5)
        last_vel = 0.05
        while not rospy.is_shutdown():
            if (len(Controller.vals_izq) == Controller.max_len) or (
                    len(Controller.vals_der == Controller.max_len)):

                rssi_izq = Controller.vals_izq[-1]
                rssi_der = Controller.vals_der[-1]
                if rssi_izq < (rssi_der - thres):
                    # move right
                    twist.angular.z = -1*max_ang
                elif rssi_der < (rssi_izq - thres):
                    # move left
                    twist.angular.z = max_ang
                else:
                    vals = zip(Controller.vals_izq, Controller.vals_der)
                    averages = [(sum(v)/2.0) for v in vals]
                    y = numpy.array(averages)
                    x = numpy.arange(Controller.max_len)
                    m = numpy.polyfit(x, y, 1)[0]
                    last_vel = -1.0*max_lin*m
                    twist.linear.x = last_vel
                    Controller.vals_izq.clear()
                    Controller.vals_der.clear()
            else:
                twist.linear.x = last_vel
                twist.angular.z = 0

            pub.publish(twist)
            rospy.spinOnce()
            rate.sleep()

        @staticmethod
        def call_izq(data):
            if data.their_mac_addr == Controller.Target_addr:
                Controller.vals_izq.append(int(data.rssi))

        @staticmethod
        def call_der(data):
            if data.their_mac_addr == Controller.Target_addr:
                Controller.vals_der.append(int(data.rssi))
