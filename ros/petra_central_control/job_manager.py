#!/usr/bin/env python3

import os
import rclpy
from rclpy.node import Node

import requests
from petra_interfaces.srv import GetTransport
from petra_interfaces.srv import UpdateTransport
from petra_interfaces.msg import PatientState
from petra_central_control.fleet_manager import FleetManager
from flask_webserver.schemas.enums import TransportStatus
from std_msgs.msg import Bool


class JobManager(Node):

    def __init__(self):
        super().__init__('job_manager')

        self.flask_webserver_url = f"{os.environ['FLASK_BACKEND_URL']}/"

        self.fleet_manager_ = FleetManager(self.flask_webserver_url)

        self.srv = self.create_service(
            GetTransport, 'GetTransport', self.get_transport_callback)
        self.srv = self.create_service(
            UpdateTransport, 'UpdateTransport', self.update_transport_callback)
        
        self.emergency_pub = self.create_publisher(PatientState, 'patient_state', 10)
        self.pause_pub = self.create_publisher(Bool, 'pause', 10)
        self.timer = self.create_timer(0.5, self.timer_callback)

        self.transport = None

        self.get_logger().info("Started job_manager")

    def timer_callback(self):
        if self.transport == None:
            return
        
        current_status = requests.get(self.flask_webserver_url +
                             "transport/" + str(self.transport["_id"])).json()["status"]
        
        self.get_logger().info('Current transport %d has state %d' % (self.transport["_id"], current_status))

        if current_status == TransportStatus.EMERGENCY_PENDING.value or current_status == TransportStatus.EMERGENCY_STOP.value:
            msg = PatientState()
            msg.state = 1
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "tablet"
            self.emergency_pub.publish(msg)
            pause_msg = Bool()
            pause_msg.data = True
            self.pause_pub.publish(pause_msg)
            self.get_logger().info("EMERGENCY FROM TABLET!")
        else:
            pause_msg = Bool()
            pause_msg.data = False
            self.pause_pub.publish(pause_msg)

    def get_transport_callback(self, request, response):
        self.get_logger().info('Incoming request id: %d' % (request.id))

        if request.id == 0:
            self.transport = self.fleet_manager_.get_optimal_next_transport()

            if self.transport == None:
                self.get_logger().error("No new transport is available")
                return response

        else:
            r = requests.get(self.flask_webserver_url +
                             "transport/" + str(request.id))
            self.transport = r.json()

            if r.status_code != 200:
                self.get_logger().error("Transport with id: %d doesn't exist" % (request.id))
                return response

        payload = requests.get(self.flask_webserver_url +
                               f"payload/{self.transport['payload']}").json()
        start_location = requests.get(self.flask_webserver_url +
                               f"location/{payload['location']}").json()
        goal_location = requests.get(self.flask_webserver_url +
                              f"location/{self.transport['goal_location']}").json()

        response.data.id = self.transport["_id"]
        response.data.status = self.transport["status"]
        response.data.mode = payload["preferred_mode"]
        response.data.name = payload["name"]
        if "last_name" in payload:
            response.data.last_name = payload["last_name"]
        if "preferred_language" in payload:
            response.data.language = payload["preferred_language"]
        if self.transport["is_start_time"]:
            print(int(self.transport["time_stamp"]/1000))
            response.data.start_time = rclpy.time.Time(seconds=int(self.transport["time_stamp"]/1000)).to_msg()
        else:
            response.data.goal_time = self.transport["time_stamp"]
        if "platform_nr" in self.transport:
            response.data.platform_nr = int(self.transport["platform_nr"])

        response.data.start_location.unique_name = start_location["name"]
        response.data.start_location.type = start_location["type"]
        response.data.start_location.x = float(start_location["position_x"])
        response.data.start_location.y = float(start_location["position_y"])
        response.data.start_location.floor = start_location["floor"]

        if "quaternion_x" in start_location:
            response.data.start_location.quaternion_x = float(
                start_location["quaternion_x"])
        if "quaternion_y" in start_location:
            response.data.start_location.quaternion_y = float(
                start_location["quaternion_y"])
        if "quaternion_z" in start_location:
            response.data.start_location.quaternion_z = float(
                start_location["quaternion_z"])
        if "quaternion_w" in start_location:
            response.data.start_location.quaternion_w = float(
                start_location["quaternion_w"])

        response.data.goal_location.unique_name = goal_location["name"]
        response.data.goal_location.type = goal_location["type"]
        response.data.goal_location.x = float(goal_location["position_x"])
        response.data.goal_location.y = float(goal_location["position_y"])
        response.data.goal_location.floor = goal_location["floor"]

        if "quaternion_x" in goal_location:
            response.data.goal_location.quaternion_x = float(
                goal_location["quaternion_x"])
        if "quaternion_y" in goal_location:
            response.data.goal_location.quaternion_y = float(
                goal_location["quaternion_y"])
        if "quaternion_z" in goal_location:
            response.data.goal_location.quaternion_z = float(
                goal_location["quaternion_z"])
        if "quaternion_w" in goal_location:
            response.data.goal_location.quaternion_w = float(
                goal_location["quaternion_w"])

        return response

    def update_transport_callback(self, request, response):

        self.get_logger().info('Incoming request id: %d' % (request.data.id))

        r = requests.get(self.flask_webserver_url +
                         "transport/" + str(request.data.id))

        if r.status_code != 200:
            self.get_logger().error("Transport with id: %d doesn't exist" % (request.data.id))
            response.success = False
            return response

        for key in request.updated_keys:
            if key == "status":
                requests.patch(self.flask_webserver_url + "transport/" +
                               str(request.data.id), json={key: request.data.status})
            elif key == "mode":
                requests.patch(self.flask_webserver_url + "transport/" +
                               str(request.data.id), json={key: request.data.mode})
            elif key == "platform_nr":
                requests.patch(self.flask_webserver_url + "transport/" +
                               str(request.data.id), json={key: request.data.platform_nr})
            else:
                self.get_logger().error(
                    "updated key not known in database or not supposed to update after transport started" % (key))

        response.success = True

        return response


def main(args=None):

    rclpy.init(args=args)

    node = JobManager()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("KeyboardInterrupt")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
