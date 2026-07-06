FROM ros:jazzy-ros-base

RUN apt-get update && apt-get install -y python3-pip python3-colcon-common-extensions
RUN pip3 install firebase-admin fastapi uvicorn --break-system-packages

WORKDIR /cloudbot

COPY ros2_ws/ /cloudbot/ros2_ws/
COPY dashboard/ /cloudbot/dashboard/

WORKDIR /cloudbot/ros2_ws
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && colcon build"

WORKDIR /cloudbot
# CHANGED: Wrapped the two execution commands in parentheses so they BOTH get the sourced environment!
CMD ["/bin/bash", "-c", "source /opt/ros/jazzy/setup.bash && source ros2_ws/install/setup.bash && (python3 dashboard/app.py & ros2 launch cloudbot_core cloudbot_launch.py)"]