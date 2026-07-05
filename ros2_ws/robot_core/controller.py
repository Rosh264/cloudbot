from movement import Movement
from planner import Planner


class Controller:

    @staticmethod
    def execute(robot, world, command):

        if command == "forward":
            Movement.move_forward(robot, world)

        elif command == "backward":
            Movement.move_backward(robot, world)

        elif command == "left":
            Movement.move_left(robot, world)

        elif command == "right":
            Movement.move_right(robot, world)

        elif command == "status":
            robot.status()

        elif command == "auto":

            path = Planner.bfs(

                world,

                robot.position,

                world.goal

            )

            print()

            print("Shortest Path")

            for step in path:

                print(step)

            print()

        else:

            print("Invalid Command")