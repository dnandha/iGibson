#!/usr/bin/python
import os
import rospy
from std_msgs.msg import Header
from geometry_msgs.msg import PoseStamped, Twist
from sensor_msgs import point_cloud2 as pc2
from sensor_msgs.msg import CameraInfo, PointCloud2
from sensor_msgs.msg import Image as ImageMsg
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
import rospkg
import numpy as np
from cv_bridge import CvBridge
import tf
from gibson2.envs.igibson_env import iGibsonEnv


class SimNode:
    def __init__(self):
        self.env = None
        self.robot = None
        self.valid_joints = None

        rospy.init_node('gibson2_sim')
        rospack = rospkg.RosPack()
        path = rospack.get_path('gibson2-ros')
        config_filename = os.path.join(path, 'tiago_dual.yaml')

        self.cmdx = 0.0
        self.cmdy = 0.0

        self.image_pub = rospy.Publisher(
            "/gibson_ros/camera/points", PointCloud2, queue_size=10)

        rospy.Subscriber(
            "/joint_states", JointState, self.cmd_callback)

        self.bridge = CvBridge()
        self.br = tf.TransformBroadcaster()

        self.env = iGibsonEnv(config_file=config_filename,
                              mode='headless',
                              action_timestep=1 / 30.0)    # assume a 30Hz simulation
        self.robot = self.env.robots[0]
        self.valid_joints = {j.joint_name: j.joint_index for j in self.robot.ordered_joints}
        self.env.reset()

        self.tp_time = None

    def run(self):
        while not rospy.is_shutdown():
            pass
            #obs, _, _, _ = self.env.step([self.cmdx, self.cmdy])
            #rgb = (obs["rgb"] * 255).astype(np.uint8)
            #normalized_depth = obs["depth"].astype(np.float32)
            #depth = normalized_depth * self.env.sensors['vision'].depth_high
            #depth_raw_image = (obs["depth"] * 1000).astype(np.uint16)

            #image_message = self.bridge.cv2_to_imgmsg(
            #    rgb, encoding="rgb8")
            #depth_message = self.bridge.cv2_to_imgmsg(
            #    depth, encoding="passthrough")
            #depth_raw_message = self.bridge.cv2_to_imgmsg(
            #    depth_raw_image, encoding="passthrough")

            #now = rospy.Time.now()

            #image_message.header.stamp = now
            #depth_message.header.stamp = now
            #depth_raw_message.header.stamp = now
            #image_message.header.frame_id = "camera_depth_optical_frame"
            #depth_message.header.frame_id = "camera_depth_optical_frame"
            #depth_raw_message.header.frame_id = "camera_depth_optical_frame"

            #self.image_pub.publish(image_message)
            #self.depth_pub.publish(depth_message)
            #self.depth_raw_pub.publish(depth_raw_message)

            #msg = CameraInfo(height=256,
            #                 width=256,
            #                 distortion_model="plumb_bob",
            #                 D=[0.0, 0.0, 0.0, 0.0, 0.0],
            #                 K=[128, 0.0, 128, 0.0, 128, 128, 0.0, 0.0, 1.0],
            #                 R=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
            #                 P=[128, 0.0, 128, 0.0, 0.0, 128, 128, 0.0, 0.0, 0.0, 1.0, 0.0])
            #msg.header.stamp = now
            #msg.header.frame_id = "camera_depth_optical_frame"
            #self.camera_info_pub.publish(msg)

            #if (self.tp_time is None) or ((self.tp_time is not None) and
            #                              ((rospy.Time.now() - self.tp_time).to_sec() > 1.)):
            #    scan = obs['scan']

    def cmd_callback(self, data):
        if self.valid_joints is None:
            return

        #for name, pos in zip(data.name, data.position):
        #    if name in self.valid_joints:
        #        print(name, pos)

    def tp_robot_callback(self, data):
        rospy.loginfo('Teleporting robot')
        position = [data.pose.position.x,
                    data.pose.position.y, data.pose.position.z]
        orientation = [
            data.pose.orientation.x, data.pose.orientation.y, data.pose.orientation.z,
            data.pose.orientation.w
        ]
        self.env.robots[0].reset_new_pose(position, orientation)
        self.tp_time = rospy.Time.now()


if __name__ == '__main__':
    node = SimNode()
    node.run()
