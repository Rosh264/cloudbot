from cloudbot_core.sensor import Sensor
class Movement:

    @staticmethod
    def move(robot, world, row_change, col_change):

        new_row = robot.position[0] + row_change
        new_col = robot.position[1] + col_change

        if world.can_move(new_row, new_col):

            robot.position[0] = new_row
            robot.position[1] = new_col

            robot.consume_battery()

        else:

            print("🚧 Movement Blocked")

    @staticmethod
    def move_forward(robot, world):
        Movement.move(robot, world, -1, 0)

    @staticmethod
    def move_backward(robot, world):
        Movement.move(robot, world, 1, 0)

    @staticmethod
    def move_left(robot, world):
        Movement.move(robot, world, 0, -1)

    @staticmethod
    def move_right(robot, world):
        Movement.move(robot, world, 0, 1)