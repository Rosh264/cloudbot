import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
import random

from cloudbot_core.robot import Robot
from cloudbot_core.world import World
from cloudbot_core.movement import Movement
from cloudbot_core.planner import Planner

# NEW: Import Cloud Database libraries
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os

class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller_node')
        
        self.robot = Robot()
        self.world = World()
        
        self.obstacle_detected = False
        
        # 1. Command Subscriber (Listens for driving commands)
        self.command_subscription = self.create_subscription(
            String,
            '/cloudbot/commands',
            self.command_callback,
            10
        )
        
        # 2. Sensor Subscriber (Listens for obstacles)
        self.sensor_subscription = self.create_subscription(
            Bool,
            '/cloudbot/obstacles',
            self.sensor_callback,
            10
        )
        
        # 3. NEW: Telemetry Publisher (Shouts battery & position to the world)
        self.telemetry_publisher = self.create_publisher(
            String, 
            '/cloudbot/telemetry', 
            10
        )
        
        self.get_logger().info("🤖 CloudBot Controller Node Ready.")
        self.world.display(self.robot)

        # NEW: Initialize Firebase (Mock or Real)
        self.db = None
        try:
            if os.path.exists("firebase_key.json"):
                cred = credentials.Certificate("firebase_key.json")
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.get_logger().info("☁️ FIREBASE CONNECTED: Logging to cloud.")
            else:
                self.get_logger().warning("☁️ FIREBASE MOCK MODE: 'firebase_key.json' not found. Simulating cloud logs.")
        except Exception as e:
            self.get_logger().error(f"Firebase init error: {e}")

    def sensor_callback(self, msg):
        self.obstacle_detected = msg.data

    def command_callback(self, msg):
        command = msg.data.lower()
        
        # ==========================================
        # ⚡ NEW: RECHARGE COMMAND ADDED HERE ⚡
        # ==========================================
        if command == "recharge":
            self.robot.battery = 100
            self.get_logger().info("⚡ Battery Recharged to 100%")
            # Instantly update the web dashboard
            telemetry_msg = String()
            telemetry_msg.data = f"Battery: {self.robot.battery}% | Position: {self.robot.position}"
            self.telemetry_publisher.publish(telemetry_msg)
            return
        # ==========================================
        
        # 1. NEW: OUT OF BATTERY CHECK
        if self.robot.battery <= 0 and command in ["forward", "backward", "left", "right"]:
            self.get_logger().error("🪫 OUT OF BATTERY! CloudBot is dead.")
            return 
            
        # 2. EXISTING: SAFETY OVERRIDE
        if self.obstacle_detected and command in ["forward", "backward", "left", "right"]:
            self.get_logger().error("🛑 EMERGENCY STOP: Obstacle detected! Waiting for clear path...")
            return 
            
        self.get_logger().info(f"Executing: {command}")
        
        # Normal movement logic
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
            path = Planner.bfs(self.world, self.robot.position, self.world.goal)
            self.get_logger().info(f"Shortest Path calculated: {path}")
        else:
            self.get_logger().warning("Invalid Command")

        self.world.display(self.robot)
        
        # NEW: Create a string with our data and publish it to the network!
        telemetry_msg = String()
        telemetry_msg.data = f"Battery: {self.robot.battery}% | Position: {self.robot.position}"
        self.telemetry_publisher.publish(telemetry_msg)
        
        # NEW: Log to Firebase Cloud!
        log_data = {
            "command": command,
            "battery": self.robot.battery,
            "position": self.robot.position,
            "timestamp": datetime.datetime.now().isoformat()
        }
        if self.db:
            self.db.collection("robot_telemetry").add(log_data)
            self.get_logger().info("☁️ Logged to Firebase Firestore.")
        else:
            self.get_logger().info(f"☁️ [MOCK CLOUD LOG]: Saved {log_data}")
        
        # Check win condition
        if self.world.reached_goal(self.robot):
            self.get_logger().info(f"📦 Package Delivered at {self.world.goal}!")
            
            # Generate a new random goal that isn't the current position
            new_goal = self.world.goal
            while new_goal == self.world.goal or new_goal == self.robot.position:
                new_goal = [random.randint(0, 4), random.randint(0, 4)]
                
            self.world.goal = new_goal
            self.get_logger().info(f"📍 New Assignment Received: Proceed to {self.world.goal}")

def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Manual shutdown triggered.")
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()