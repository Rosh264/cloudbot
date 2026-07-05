import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import threading

# 1. Global variable to store the latest robot data
latest_telemetry = "Waiting for robot data..."

# 2. A tiny ROS 2 Node just to listen to the robot's walkie-talkie
class DashboardListener(Node):
    def __init__(self):
        super().__init__('dashboard_listener')
        # Listen to the exact same topic the controller is publishing to!
        self.subscription = self.create_subscription(
            String, '/cloudbot/telemetry', self.listener_callback, 10
        )

    def listener_callback(self, msg):
        global latest_telemetry
        # When a message arrives, save it to our global variable
        latest_telemetry = msg.data  

# 3. Create the Web App using FastAPI
app = FastAPI()

@app.get("/")
@app.get("/")
def get_dashboard():
    html_content = f"""
    <html>
        <head><meta http-equiv="refresh" content="1"></head>
        <body style="text-align: center; font-family: Arial; margin-top: 50px; background-color: #f4f4f9;">
            <h1>🤖 CloudBot Web Dashboard</h1>
            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 8px rgba(0,0,0,0.2); display: inline-block;">
                <h2>Live Telemetry:</h2>
                <p style="font-size: 24px; color: #0078D7; font-weight: bold;">{latest_telemetry}</p>
            </div>
            <p><small>Live updating every second...</small></p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# 4. Start everything up
def start_ros():
    rclpy.init()
    node = DashboardListener()
    rclpy.spin(node) # Keeps ROS 2 listening forever

if __name__ == "__main__":
    # Python Trick: ROS 2 and FastAPI both want to run "forever".
    # We put ROS 2 in a background thread so they can run at the same time.
    threading.Thread(target=start_ros, daemon=True).start()
    
    # Start the Web Server
    uvicorn.run(app, host="0.0.0.0", port=8000)