class World:

    def __init__(self):

        self.rows = 5
        self.cols = 5

        self.goal = [4, 4]

        self.obstacles = [

            [1, 2],
            [3, 3]

        ]

    def display(self, robot):

        print()

        for row in range(self.rows):

            for col in range(self.cols):

                if [row, col] == robot.position:

                    print("R", end=" ")

                elif [row, col] == self.goal:

                    print("G", end=" ")

                elif [row, col] in self.obstacles:

                    print("X", end=" ")

                else:

                    print(".", end=" ")

            print()

        print()

    def can_move(self, row, col):

        if row < 0 or row >= self.rows:
            return False

        if col < 0 or col >= self.cols:
            return False

        if [row, col] in self.obstacles:
            return False

        return True

    def reached_goal(self, robot):

        return robot.position == self.goal

    def get_neighbors(self, row, col):

        neighbors = []

        directions = [

            (-1, 0),   # Up
            (1, 0),    # Down
            (0, -1),   # Left
            (0, 1)     # Right

        ]

        for dr, dc in directions:

            new_row = row + dr
            new_col = col + dc

            if self.can_move(new_row, new_col):
                neighbors.append([new_row, new_col])

        return neighbors