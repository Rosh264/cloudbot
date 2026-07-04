class World:

    def __init__(self):

        self.size = 5

        self.grid = [

            [".", ".", ".", ".", "."],
            [".", ".", "X", ".", "."],
            ["R", ".", ".", ".", "."],
            [".", ".", ".", "X", "."],
            [".", ".", ".", ".", "G"]

        ]

    def display(self):

        print()

        for row in self.grid:
            print(" ".join(row))

        print()