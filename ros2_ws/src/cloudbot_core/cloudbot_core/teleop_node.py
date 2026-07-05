import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import sys
import termios
import tty

# 1. Dictionary mapping your keyboard to robot commands
KEY_MAP = {
    'w': 'forward',
    's': 'backward',
    'a': 'left',
    'd': 'right',
    'q': 'status',
    'e': 'auto'
}

class TeleopNode(Node):
    def __init__(self):
        super().__init__('teleop_node')
        
        # 2. Create a Publisher (Notice it matches the Subscriber topic exactly)
        self.publisher_ = self.create_publisher(String, '/cloudbot/commands', 10)
        
        print("\n🎮 CloudBot Teleop Ready!")
        print("---------------------------")
        print("  W : Forward")
        print("A S D : Left / Backward / Right")
        print("  Q : Status   |   E : Auto-Solve")
        print("---------------------------")
        print("Press CTRL+C to Quit\n")

    def publish_command(self, cmd_str):
        # 3. Create the message envelope, put the string inside, and publish
        msg = String()
        msg.data = cmd_str
        self.publisher_.publish(msg)

# 4. Helper function to read a single keypress without hitting 'Enter'
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main(args=None):
    rclpy.init(args=args)
    node = TeleopNode()

    try:
        # 5. Continuous loop listening for keystrokes
        while rclpy.ok():
            key = get_key()
            
            # \x03 is the ASCII code for CTRL+C
            if key == '\x03': 
                break
                
            # If the key is in our map, publish the command
            if key in KEY_MAP:
                node.publish_command(KEY_MAP[key])
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean shutdown
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()