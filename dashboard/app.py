import os
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
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

app = FastAPI(title="CloudBot Command Center")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def get_dashboard():
    global latest_telemetry
    
    rob_r, rob_c = 0, 0
    battery = 100
    has_obstacle = False
    
    if "Position:" in latest_telemetry:
        try:
            pos_str = latest_telemetry.split("Position: [")[1].split("]")[0]
            r_str, c_str = pos_str.split(",")
            rob_r, rob_c = int(r_str.strip()), int(c_str.strip())
        except:
            pass
            
    if "Battery: " in latest_telemetry:
        try:
            battery = int(latest_telemetry.split("Battery: ")[1].split("%")[0])
        except:
            pass
            
    # ⚡ BUG 2 FIX: Parse the new obstacle flag from the backend payload
    if "Obstacle: True" in latest_telemetry:
        has_obstacle = True

    # ⚡ BUG 2 FIX: Conditionally render a highly visible banner if an obstacle blocks the path
    obstacle_banner = ""
    if has_obstacle:
        obstacle_banner = '<div style="background-color: #f38ba8; color: #11111b; font-weight: bold; padding: 12px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">🚧 Obstacle Detected on Backend!</div>'
            
    grid_html = '<div style="display: grid; grid-template-columns: repeat(5, 50px); gap: 4px; justify-content: center; margin-bottom: 20px;">'
    for r in range(5):
        for c in range(5):
            is_robot = (r == rob_r and c == rob_c)
            bg = "#a6e3a1" if is_robot else "#1e1e2e"
            icon = '<img src="/static/logo.png" width="40" style="border-radius: 8px;">' if is_robot else ""
            grid_html += f'<div style="width: 50px; height: 50px; background: {bg}; border-radius: 5px; display: flex; align-items: center; justify-content: center; border: 1px solid #45475a;">{icon}</div>'
    grid_html += '</div>'
    
    if battery <= 15:
        battery_color = "#f38ba8" 
    elif battery <= 30:
        battery_color = "#fab387" 
    else:
        battery_color = "#a6e3a1" 

    html_content = f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="1">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CloudBot Dashboard</title>
            <link rel="icon" type="image/png" href="/static/logo.png">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e2e; color: #cdd6f4; text-align: center; margin-top: 30px; margin-bottom: 50px; overflow-x: hidden; }}
                h1 {{ color: #89b4fa; font-size: 32px; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; gap: 15px; flex-wrap: wrap; }}
                .main-container {{ display: flex; flex-direction: column; align-items: center; gap: 20px; justify-content: center; padding: 0 15px; }}
                @media (min-width: 768px) {{
                    .main-container {{ flex-direction: row; align-items: stretch; }}
                    .controls-card {{ order: -1; }}
                }}
                .card {{ background: #313244; padding: 25px; border-radius: 12px; box-shadow: 0px 8px 15px rgba(0,0,0,0.3); border: 1px solid #45475a; width: 100%; max-width: 350px; display: flex; flex-direction: column; justify-content: center; }}
                .telemetry {{ font-size: 18px; color: {battery_color}; font-weight: bold; margin: 15px 0; }}
                .d-pad {{ display: grid; grid-template-columns: repeat(3, 80px); gap: 10px; justify-content: center; margin-top: 20px; }}
                .btn {{ padding: 20px 0; background: #89b4fa; color: #11111b; font-weight: bold; border-radius: 8px; cursor: pointer; border: none; font-size: 16px; transition: 0.2s; }}
                .btn:hover {{ background: #b4befe; }}
                .btn:active {{ transform: scale(0.95); }}
                .up {{ grid-column: 2; }}
                .left {{ grid-column: 1; }}
                .down {{ grid-column: 2; }}
                .right {{ grid-column: 3; }}
                .recharge-btn {{ background: #a6e3a1; grid-column: 1 / span 3; margin-top: 10px; }}
                .recharge-btn:hover {{ background: #94e2d5; }}
                #toast {{ visibility: hidden; min-width: 250px; background-color: #f38ba8; color: #11111b; text-align: center; border-radius: 8px; padding: 16px; position: fixed; z-index: 1; left: 50%; bottom: 30px; transform: translateX(-50%); font-weight: bold; font-size: 16px; opacity: 0; transition: opacity 0.3s, bottom 0.3s; box-shadow: 0px 4px 10px rgba(0,0,0,0.5); }}
                #toast.show {{ visibility: visible; opacity: 1; bottom: 50px; }}
            </style>
        </head>
        <body>
            <h1>
                <img src="/static/logo.png" width="60" style="border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.4);">
                CloudBot Command Center
            </h1>
            
            <div class="main-container">
                <div class="card telemetry-card">
                    <h2 style="color: #bac2de; margin: 0; margin-bottom: 10px;">Live Telemetry</h2>
                    {obstacle_banner}
                    <div class="telemetry">Battery: {battery}% | Position: [{rob_r}, {rob_c}]</div>
                    {grid_html}
                </div>
                
                <div class="card controls-card">
                    <h2 style="color: #bac2de; margin: 0;">Remote Control</h2>
                    <p style="color: #a6adc8; font-size: 14px;">Use <b>W A S D</b> or tap the buttons.</p>
                    
                    <div class="d-pad">
                        <button class="btn up" onclick="sendCommand('forward')">W</button>
                        <button class="btn left" onclick="sendCommand('left')">A</button>
                        <button class="btn down" onclick="sendCommand('backward')">S</button>
                        <button class="btn right" onclick="sendCommand('right')">D</button>
                        <button class="btn recharge-btn" onclick="sendCommand('recharge')">⚡ RECHARGE ⚡</button>
                    </div>
                </div>
            </div>

            <div id="toast">🚧 Boundary Detected!</div>

            <script>
                const currentR = {rob_r};
                const currentC = {rob_c};
                let isToastVisible = false;

                function showToast(message) {{
                    if (isToastVisible) return;
                    isToastVisible = true;
                    const toast = document.getElementById("toast");
                    toast.innerText = message;
                    toast.className = "show";
                    setTimeout(function() {{
                        toast.className = toast.className.replace("show", "");
                        isToastVisible = false;
                    }}, 2000);
                }}

                function sendCommand(direction) {{
                    if (direction === 'forward' && currentR === 0) {{ showToast("🚧 Boundary! Cannot move forward."); return; }}
                    if (direction === 'backward' && currentR === 4) {{ showToast("🚧 Boundary! Cannot move backward."); return; }}
                    if (direction === 'left' && currentC === 0) {{ showToast("🚧 Boundary! Cannot move left."); return; }}
                    if (direction === 'right' && currentC === 4) {{ showToast("🚧 Boundary! Cannot move right."); return; }}

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