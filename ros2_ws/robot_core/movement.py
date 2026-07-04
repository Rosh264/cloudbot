from sensor import Sensor
class Movement:

    @staticmethod
    def move_forward(robot):

        if Sensor.obstacle_detected():
            print("🚧 Obstacle Ahead!")
            return

        robot.position[1] += 1
        robot.consume_battery()

    @staticmethod
    def move_backward(robot):
        robot.position[1] -= 1
        robot.consume_battery()

    @staticmethod
    def move_left(robot):
        robot.position[0] -= 1
        robot.consume_battery()

    @staticmethod
    def move_right(robot):
        robot.position[0] += 1
        robot.consume_battery()