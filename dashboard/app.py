import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import threading

latest_telemetry = "Waiting for robot data..."
ros_node = None 

class WebControllerNode(Node):
    def __init__(self):
        super().__init__('web_controller_node')
        self.subscription = self.create_subscription(String, '/cloudbot/telemetry', self.listener_callback, 10)
        self.publisher = self.create_publisher(String, '/cloudbot/commands', 10)

    def listener_callback(self, msg):
        global latest_telemetry
        latest_telemetry = msg.data  

    def send_command(self, cmd):
        msg = String()
        msg.data = cmd
        self.publisher.publish(msg)

app = FastAPI()

@app.get("/")
def get_dashboard():
    # Parse position for the live grid!
    rob_r, rob_c = 0, 0
    if "Position: [" in latest_telemetry:
        try:
            pos_str = latest_telemetry.split("Position: [")[1].split("]")[0]
            r_str, c_str = pos_str.split(",")
            rob_r, rob_c = int(r_str.strip()), int(c_str.strip())
        except:
            pass
            
    # Build a 5x5 dynamic HTML Grid
    grid_html = '<div style="display: grid; grid-template-columns: repeat(5, 50px); gap: 4px; justify-content: center; margin-bottom: 20px;">'
    for r in range(5):
        for c in range(5):
            is_robot = (r == rob_r and c == rob_c)
            bg = "#a6e3a1" if is_robot else "#1e1e2e"
            icon = "🤖" if is_robot else ""
            grid_html += f'<div style="width: 50px; height: 50px; background: {bg}; border-radius: 5px; display: flex; align-items: center; justify-content: center; font-size: 24px; border: 1px solid #45475a;">{icon}</div>'
    grid_html += '</div>'

    html_content = f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="1">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e2e; color: #cdd6f4; text-align: center; margin-top: 50px; }}
                h1 {{ color: #89b4fa; font-size: 36px; margin-bottom: 30px; }}
                .card {{ background: #313244; padding: 25px; border-radius: 12px; box-shadow: 0px 8px 15px rgba(0,0,0,0.3); display: inline-block; margin-bottom: 25px; border: 1px solid #45475a; }}
                .telemetry {{ font-size: 26px; color: #a6e3a1; font-weight: bold; margin: 15px 0; }}
                .d-pad {{ display: grid; grid-template-columns: repeat(3, 80px); gap: 10px; justify-content: center; margin-top: 20px; }}
                .btn {{ padding: 20px 0; background: #89b4fa; color: #11111b; font-weight: bold; border-radius: 8px; cursor: pointer; text-decoration: none; border: none; font-size: 16px; transition: 0.2s; }}
                .btn:hover {{ background: #b4befe; }}
                .btn:active {{ transform: scale(0.95); }}
                .up {{ grid-column: 2; }}
                .left {{ grid-column: 1; }}
                .down {{ grid-column: 2; }}
                .right {{ grid-column: 3; }}
            </style>
        </head>
        <body>
            <h1>🤖 CloudBot Command Center</h1>
            
            <div class="card">
                <h2 style="color: #bac2de; margin: 0;">Live Telemetry</h2>
                <div class="telemetry">{latest_telemetry}</div>
                {grid_html}
            </div>
            
            <br>
            
            <div class="card">
                <h2 style="color: #bac2de; margin: 0;">Remote Control</h2>
                <p style="color: #a6adc8; font-size: 14px;">Use <b>W A S D</b> on your keyboard!</p>
                
                <div class="d-pad">
                    <button class="btn up" onclick="sendCommand('forward')">W</button>
                    <button class="btn left" onclick="sendCommand('left')">A</button>
                    <button class="btn down" onclick="sendCommand('backward')">S</button>
                    <button class="btn right" onclick="sendCommand('right')">D</button>
                </div>
            </div>

            <script>
                function sendCommand(direction) {{
                    fetch('/move/' + direction);
                }}

                document.addEventListener('keydown', function(event) {{
                    const keyMap = {{ 'w': 'forward', 'a': 'left', 's': 'backward', 'd': 'right' }};
                    const cmd = keyMap[event.key.toLowerCase()];
                    if (cmd) {{
                        sendCommand(cmd);
                    }}
                }});
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/move/{direction}")
def move_robot(direction: str):
    if ros_node:
        ros_node.send_command(direction)
    return {"status": "success"}

def start_ros():
    global ros_node
    rclpy.init()
    ros_node = WebControllerNode()
    rclpy.spin(ros_node)

if __name__ == "__main__":
    threading.Thread(target=start_ros, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)