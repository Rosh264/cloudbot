import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
import random
import datetime
import os

from cloudbot_core.robot import Robot
from cloudbot_core.world import World
from cloudbot_core.movement import Movement
from cloudbot_core.planner import Planner

# Cloud Database libraries
import firebase_admin
from firebase_admin import credentials, firestore

class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller_node')
        
        self.robot = Robot()
        self.world = World()
        
        self.obstacle_detected = False
        self.collision_countdown = 0  
        
        # Subscribers & Publishers
        self.command_subscription = self.create_subscription(String, '/cloudbot/commands', self.command_callback, 10)
        self.sensor_subscription = self.create_subscription(Bool, '/cloudbot/obstacles', self.sensor_callback, 10)
        self.telemetry_publisher = self.create_publisher(String, '/cloudbot/telemetry', 10)
        
        # The Heartbeat Timer (Runs every 1 second)
        self.telemetry_timer = self.create_timer(1.0, self.publish_telemetry)
        
        self.get_logger().info("🤖 CloudBot Controller Node Ready.")
        self.world.display(self.robot)

        # Initialize Firebase
        self.db = None
        try:
            if os.path.exists("firebase_key.json"):
                cred = credentials.Certificate("firebase_key.json")
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.get_logger().info("☁️ FIREBASE CONNECTED.")
        except Exception as e:
            pass

    def sensor_callback(self, msg):
        self.obstacle_detected = msg.data
        self.publish_telemetry()

    def command_callback(self, msg):
        command = msg.data.lower()
        
        if command == "recharge":
            self.robot.battery = 100
            self.publish_telemetry()
            return
        
        if self.robot.battery <= 0 and command in ["forward", "backward", "left", "right"]:
            return 
            
        if self.obstacle_detected and command in ["forward", "backward", "left", "right"]:
            return 
            
        # Capture previous position before moving
        prev_pos = list(self.robot.position)
        
        if command == "forward":
            Movement.move_forward(self.robot, self.world)
        elif command == "backward":
            Movement.move_backward(self.robot, self.world)
        elif command == "left":
            Movement.move_left(self.robot, self.world)
        elif command == "right":
            Movement.move_right(self.robot, self.world)
        elif command == "status":
            self.robot.status()
        elif command == "auto":
            Planner.bfs(self.world, self.robot.position, self.world.goal)

        # Check if the robot hit a fixed obstacle (position didn't change)
        if command in ["forward", "backward", "left", "right"]:
            if self.robot.position == prev_pos:
                self.collision_countdown = 3  

        self.world.display(self.robot)
        self.publish_telemetry()
        
        # Firebase logging
        log_data = {
            "command": command,
            "battery": self.robot.battery,
            "position": self.robot.position,
            "timestamp": datetime.datetime.now().isoformat()
        }
        if self.db:
            self.db.collection("robot_telemetry").add(log_data)
        
        if self.world.reached_goal(self.robot):
            new_goal = self.world.goal
            while new_goal == self.world.goal or new_goal == self.robot.position:
                new_goal = [random.randint(0, 4), random.randint(0, 4)]
            self.world.goal = new_goal

    def publish_telemetry(self):
        # Determine if ANY obstacle flag should be raised (Sensor OR Fixed Collision)
        is_blocked = self.obstacle_detected or (self.collision_countdown > 0)
        
        telemetry_msg = String()
        telemetry_msg.data = f"Battery: {self.robot.battery}% | Position: {self.robot.position} | Obstacle: {is_blocked}"
        self.telemetry_publisher.publish(telemetry_msg)
        
        # Decrement the transient state timer safely
        if self.collision_countdown > 0:
            self.collision_countdown -= 1

def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()