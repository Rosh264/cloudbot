from movement import Movement


class Controller:

    @staticmethod
    def execute(robot, command):

        if command == "forward":
            Movement.move_forward(robot)

        elif command == "backward":
            Movement.move_backward(robot)

        elif command == "left":
            Movement.move_left(robot)

        elif command == "right":
            Movement.move_right(robot)

        elif command == "status":
            robot.status()

        else:
            print("❌ Invalid Command")