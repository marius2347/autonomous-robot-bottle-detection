#!/usr/bin/env python3
import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from std_msgs.msg import Header

def publisher_without_cv_bridge():
    rospy.init_node("csi_camera_node", anonymous=True)
    pub = rospy.Publisher("camera/image", Image, queue_size=1)

    # Pipeline GStreamer cu libcamerasrc (pentru camera CSI)
    gst_pipeline = (
        "libcamerasrc ! "                               # Folosește camera CSI prin libcamera
        "video/x-raw,width=640,height=480,framerate=30/1 ! "
        "videoconvert ! queue max-size-buffers=1 leaky=2 ! "
        "video/x-raw,format=BGR ! appsink"
    )

    cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        rospy.logerr("Nu s-a putut deschide camera CSI cu pipeline-ul GStreamer (libcamerasrc)!")
        return

    rate = rospy.Rate(30)
    while not rospy.is_shutdown():
        ret, frame = cap.read()
        if not ret:
            rospy.logerr("Nu s-a putut captura frame-ul!")
            continue

        # Construim mesajul ROS de tip sensor_msgs/Image
        img_msg = Image()
        img_msg.header = Header()
        img_msg.header.stamp = rospy.Time.now()
        img_msg.height, img_msg.width = frame.shape[:2]
        img_msg.encoding = "bgr8"
        img_msg.is_bigendian = 0
        img_msg.step = img_msg.width * 3
        img_msg.data = frame.tobytes()

        pub.publish(img_msg)
        rate.sleep()

    cap.release()


publisher_without_cv_bridge()
