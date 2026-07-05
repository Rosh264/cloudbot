import sys
from robot import Robot
from controller import Controller
from world import World

robot = Robot()
world = World()

world.display(robot)

print("🤖 CloudBot Started")
print("Available Commands:")
print("forward | backward | left | right | status | auto | exit")
print("-" * 40)

# Check if the robot spawned on the goal
if world.reached_goal(robot):
    print("🎉 Congratulations! Goal Reached!")
    sys.exit(0)  # Use sys.exit() instead of break to stop the script

# Main Control Loop
while True:
    command = input(">> ").lower()

    if command == "exit":
        print("👋 Shutting Down CloudBot...")
        sys.exit(0)  # Cleanly exit the script

    Controller.execute(robot, world, command)
    world.display(robot)
    
    # Check if the last move reached the goal
    if world.reached_goal(robot):
        print("🎉 Congratulations! Goal Reached!")
        sys.exit(0)