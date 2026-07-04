import random


class Sensor:

    @staticmethod
    def obstacle_detected():

        chance = random.randint(1, 10)

        if chance <= 3:
            return True

        return False