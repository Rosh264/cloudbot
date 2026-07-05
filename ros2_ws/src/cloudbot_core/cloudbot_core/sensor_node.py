import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
import random

class SensorNode(Node):
    def __init__(self):
        super().__init__('sensor_node')
        
        # 1. Create a Publisher using the Bool message type
        self.publisher_ = self.create_publisher(Bool, '/cloudbot/obstacles', 10)
        
        # 2. Set up a timer to trigger every 2.0 seconds
        timer_period = 2.0  
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        self.get_logger().info("📡 CloudBot Sensor Node Online. Scanning for obstacles...")

    def timer_callback(self):
        # 3. Simulate hardware detection (30% chance of an obstacle)
        msg = Bool()
        chance = random.randint(1, 10)
        
        if chance <= 3:
            msg.data = True
            self.get_logger().warning("🚧 OBSTACLE DETECTED!")
        else:
            msg.data = False
            self.get_logger().info("Path clear.")
            
        # 4. Publish the sensor reading to the network
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = SensorNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Sensor shutting down.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()