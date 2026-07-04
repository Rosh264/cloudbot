class Robot:
    def __init__(self):
        self.name = "CloudBot"          # Robot name
        self.battery = 100              # Battery starts at 100%
        self.position = [0, 0]          # X,Y coordinates
        self.speed = 0                  # Current speed

    def consume_battery(self):
        if self.battery > 0:
            self.battery -= 5

    def status(self):
        print("\n===== Robot Status =====")
        print(f"Name      : {self.name}")
        print(f"Battery   : {self.battery}%")
        print(f"Position  : {self.position}")
        print(f"Speed     : {self.speed}")

