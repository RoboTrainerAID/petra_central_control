#!/usr/bin/env python3
import codecs

import rclpy
from rclpy.node import Node
from nav_msgs.srv import GetMap
from nav_msgs.msg import OccupancyGrid, Path
from geometry_msgs.msg import PoseStamped
import requests
import base64
import os
import tf_transformations

class TestMapNode(Node):

    def __init__(self):
        super().__init__('test_map_node')  # type: ignore
        self.backend_url = os.environ['FLASK_BACKEND_URL']
        self.map_service_name = os.environ['MAP_SERVICE_NAME']

        self.map_client = self.create_client(GetMap, self.map_service_name)

        self.map: OccupancyGrid = self.get_map()

        self.get_logger().info("Map loaded")

        # TODO: @Freddy Hier sind die infos die über die map bekannt sind, das wirkliche Bild liegt in 'data'

        # The time at which the map was loaded
        print(self.map.info.map_load_time)
        # The map resolution [m/cell]
        print(self.map.info.resolution)
        # Map width [cells]
        print(self.map.info.width)
        # Map height [cells]
        print(self.map.info.height)
        # The origin of the map [m, m, rad]. This is the real-world pose of the
        # bottom left corner of cell (0,0) in the map.
        print(self.map.info.origin.position.x)
        print(self.map.info.origin.position.y)
        print(self.map.info.origin.position.z)
        print(self.map.info.origin.orientation)
        # The map data, in row-major order, starting with (0,0).
        # Cell (1, 0) will be listed second, representing the next cell in the x direction.
        # Cell (0, 1) will be at the index equal to info.width, followed by (1, 1).
        # The values inside are application dependent, but frequently,
        # 0 represents unoccupied, 1 represents definitely occupied, and
        # -1 represents unknown.
        data = self.map.data

        # TODO: @Freddy mit requests.post map an flask webserver schicken. Variablen noch richtig setzen. Hier nur ein Beispiel...
        requests.post(f"{self.backend_url}/relay/map", json={
            "data": base64.b64encode(data).decode('ascii'),
            "width": self.map.info.width,
            "height": self.map.info.height,
            "resolution": self.map.info.resolution,
            "origin_x": self.map.info.origin.position.x,
            "origin_y": self.map.info.origin.position.y,
            "origin_angle": 0,  # TODO: extract angle
        })

        self.update_path = self.create_subscription(Path, 'update_path', self.update_path_callback, 10)
        self.update_path_real_robot = self.create_subscription(Path, os.environ['PATH_TOPIC_NAME'], self.update_path_callback, 10)
        self.update_pose = self.create_subscription(PoseStamped, 'update_pose', self.update_pose_callback, 10)
        self.update_pose_real_robot = self.create_subscription(PoseStamped, os.environ['POSITION_TOPIC_NAME'], self.update_pose_callback, 10)

    def get_map(self):
        while not self.map_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(self.map_service_name + ' service not available, waiting again...')

        future = self.map_client.call_async(GetMap.Request())
        rclpy.spin_until_future_complete(self, future)

        return future.result().map  # type: ignore
 
    
    def update_path_callback(self, msg):
        self.get_logger().info("Received new path")
        # An array of poses that represents a Path for a robot to follow.
        # Array of poses to follow. Orientation in quaternion
        # for p in msg.poses:
        #     print("On map:", (p.pose.position.x, p.pose.position.y), "in pixels:", self.transform_map_pos_to_graph(p))
            # print(p.pose.orientation)


        requests.post(f"{self.backend_url}/relay/path", json={"nodes": [{
            "x": p.pose.position.x,
            "y": p.pose.position.y,
            "angle": self.convert_quaternion_to_angle(p.pose.orientation)
        } for p in msg.poses]})

    def update_pose_callback(self, msg):
        self.get_logger().info("Received new robot pose")

        requests.post(f"{self.backend_url}/relay/position", json={
            "x": msg.pose.position.x,
            "y": msg.pose.position.y,
            "angle": self.convert_quaternion_to_angle(msg.pose.orientation)
        })

    def convert_quaternion_to_angle(self, orientation):
        
        roll, pitch, yaw = tf_transformations.euler_from_quaternion([orientation.x, orientation.y, orientation.z, orientation.w])

        return yaw
    
def main(args=None):

    rclpy.init(args=args)

    node = TestMapNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("KeyboardInterrupt")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
