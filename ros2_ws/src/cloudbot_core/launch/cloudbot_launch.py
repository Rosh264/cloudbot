from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Start the Controller (The Brain)
        Node(
            package='cloudbot_core',
            executable='controller',
            name='controller_node',
            output='screen'
        ),
        # 2. Start the Sensor (The Eyes)
        Node(
            package='cloudbot_core',
            executable='sensor',
            name='sensor_node',
            output='screen'
        )
    ])