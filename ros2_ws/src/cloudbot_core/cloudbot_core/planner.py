from collections import deque


class Planner:

    @staticmethod
    def bfs(world, start, goal):

        queue = deque()

        queue.append((start, [start]))

        visited = []

        while queue:

            current, path = queue.popleft()

            if current == goal:
                return path

            if current in visited:
                continue

            visited.append(current)

            neighbours = world.get_neighbors(current[0], current[1])

            for neighbour in neighbours:

                if neighbour not in visited:

                    queue.append(

                        (

                            neighbour,

                            path + [neighbour]

                        )

                    )

        return []