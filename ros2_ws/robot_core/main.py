from robot import Robot
from controller import Controller

robot = Robot()

print("🤖 CloudBot Started")
print("Available Commands:")
print("forward | backward | left | right | status | exit")
print("-" * 40)

while True:

    command = input(">> ").lower()

    if command == "exit":
        print("👋 Shutting Down CloudBot...")
        break

    Controller.execute(robot, command)