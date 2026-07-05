import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool

from cloudbot_core.robot import Robot
from cloudbot_core.world import World
from cloudbot_core.movement import Movement
from cloudbot_core.planner import Planner

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

    def sensor_callback(self, msg):
        self.obstacle_detected = msg.data

    def command_callback(self, msg):
        command = msg.data.lower()
        
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
        
        # Check win condition
        if self.world.reached_goal(self.robot):
            self.get_logger().info("🎉 Congratulations! Goal Reached! Shutting down node.")
            rclpy.shutdown()

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