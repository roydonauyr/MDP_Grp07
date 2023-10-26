from typing import List
from constants import Direction, EXPANDED_CELL, SCREENSHOT_COST
from helper import is_valid


class CellState:
    """Base class for all objects on the arena, such as cells, obstacles, etc"""

    def __init__(self, x, y, direction: Direction = Direction.NORTH, screenshot_id=-1, penalty=0):
        self.x = x
        self.y = y
        self.direction = direction
        # If screenshot_id != -1, the snapshot is taken at that position is for the obstacle with id = screenshot_id
        self.screenshot_id = screenshot_id
        self.penalty = penalty  # Penalty for the view point of taking picture

    def cmp_position(self, x, y) -> bool:
        # Compare given (x,y) position with cell state's position
        return self.x == x and self.y == y

    def is_eq(self, x, y, direction):
        # Compare given x, y, direction with cell state's position and direction
        return self.x == x and self.y == y and self.direction == direction

    def __repr__(self):
        return "x: {}, y: {}, d: {}, screenshot: {}".format(self.x, self.y, self.direction, self.screenshot_id)

    def set_screenshot(self, screenshot_id):
        self.screenshot_id = screenshot_id

    def get_dict(self):
        return {'x': self.x, 'y': self.y, 'd': self.direction, 's': self.screenshot_id}
    


class Obstacle(CellState):
    def __init__(self, x: int, y: int, direction: Direction, obstacle_id: int):
        super().__init__(x, y, direction)
        self.obstacle_id = obstacle_id

    def __eq__(self, other):
        # Checks if this obstacle is the same as input in terms of x, y, and direction

        return self.x == other.x and self.y == other.y and self.direction == other.direction

    def get_view_state(self, retrying) -> List[CellState]:
        # Constructs the list of CellStates from which the robot can view the symbol on the obstacle

        cells = []

        # If the obstacle is facing north, then robot's cell state must be facing south
        if self.direction == Direction.NORTH:
            if retrying == False:
                # Or (x, y + 3)
                if is_valid(self.x, self.y + 1 + EXPANDED_CELL * 2):
                    cells.append(CellState(
                        self.x, self.y + 1 + EXPANDED_CELL * 2, Direction.SOUTH, self.obstacle_id, 5))
                # Or (x, y + 4)
                if is_valid(self.x, self.y + 2 + EXPANDED_CELL * 2):
                    cells.append(CellState(
                        self.x, self.y + 2 + EXPANDED_CELL * 2, Direction.SOUTH, self.obstacle_id, 0))

                # Or (x + 1, y + 4)
                if is_valid(self.x + 1, self.y + 2 + EXPANDED_CELL * 2):
                    cells.append(CellState(self.x + 1, self.y + 2 + EXPANDED_CELL *
                                 2, Direction.SOUTH, self.obstacle_id, SCREENSHOT_COST))
                # Or (x - 1, y + 4)
                if is_valid(self.x - 1, self.y + 2 + EXPANDED_CELL * 2):
                    cells.append(CellState(self.x - 1, self.y + 2 + EXPANDED_CELL *
                                 2, Direction.SOUTH, self.obstacle_id, SCREENSHOT_COST))

        # If obstacle is facing south, then robot's cell state must be facing north
        elif self.direction == Direction.SOUTH:

            if retrying == False:
                # Or (x, y - 3)
                if is_valid(self.x, self.y - 1 - EXPANDED_CELL * 2):
                    cells.append(CellState(
                        self.x, self.y - 1 - EXPANDED_CELL * 2, Direction.NORTH, self.obstacle_id, 5))
                # Or (x, y - 4)
                if is_valid(self.x, self.y - 2 - EXPANDED_CELL * 2):
                    cells.append(CellState(
                        self.x, self.y - 2 - EXPANDED_CELL * 2, Direction.NORTH, self.obstacle_id, 0))

                # Or (x + 1, y - 4)
                if is_valid(self.x + 1, self.y - 2 - EXPANDED_CELL * 2):
                    cells.append(CellState(self.x + 1, self.y - 2 - EXPANDED_CELL *
                                 2, Direction.NORTH, self.obstacle_id, SCREENSHOT_COST))
                # Or (x - 1, y - 4)
                if is_valid(self.x - 1, self.y - 2 - EXPANDED_CELL * 2):
                    cells.append(CellState(self.x - 1, self.y - 2 - EXPANDED_CELL *
                                 2, Direction.NORTH, self.obstacle_id, SCREENSHOT_COST))

        # If obstacle is facing east, then robot's cell state must be facing west
        elif self.direction == Direction.EAST:

            if retrying == False:
                # Or (x + 3,y)
                if is_valid(self.x + 1 + EXPANDED_CELL * 2, self.y):
                    cells.append(CellState(self.x + 1 + EXPANDED_CELL * 2,
                                 self.y, Direction.WEST, self.obstacle_id, 5))
                # Or (x + 4,y)
                if is_valid(self.x + 2 + EXPANDED_CELL * 2, self.y):
                    # print(f"Obstacle facing east, Adding {self.x + 2 + EXPANDED_CELL * 2}, {self.y}")
                    cells.append(CellState(self.x + 2 + EXPANDED_CELL * 2,
                                 self.y, Direction.WEST, self.obstacle_id, 0))

                # Or (x + 4, y + 1)
                if is_valid(self.x + 2 + EXPANDED_CELL * 2, self.y + 1):
                    cells.append(CellState(self.x + 2 + EXPANDED_CELL * 2, self.y +
                                 1, Direction.WEST, self.obstacle_id, SCREENSHOT_COST))
                # Or (x + 4, y - 1)
                if is_valid(self.x + 2 + EXPANDED_CELL * 2, self.y - 1):
                    cells.append(CellState(self.x + 2 + EXPANDED_CELL * 2, self.y -
                                 1, Direction.WEST, self.obstacle_id, SCREENSHOT_COST))

        # If obstacle is facing west, then robot's cell state must be facing east
        elif self.direction == Direction.WEST:
            # It can be (x - 2,y)
            # if is_valid(self.x - EXPANDED_CELL * 2, self.y):
            #     cells.append(CellState(self.x - EXPANDED_CELL * 2, self.y, Direction.EAST, self.obstacle_id, 0))

            if retrying == False:
                # Or (x - 3, y)
                if is_valid(self.x - 1 - EXPANDED_CELL * 2, self.y):
                    cells.append(CellState(self.x - 1 - EXPANDED_CELL * 2,
                                 self.y, Direction.EAST, self.obstacle_id, 5))
                # Or (x - 4, y)
                if is_valid(self.x - 2 - EXPANDED_CELL * 2, self.y):
                    cells.append(CellState(self.x - 2 - EXPANDED_CELL * 2,
                                 self.y, Direction.EAST, self.obstacle_id, 0))

                # Or (x - 4, y + 1)
                if is_valid(self.x - 2 - EXPANDED_CELL * 2, self.y + 1):
                    cells.append(CellState(self.x - 2 - EXPANDED_CELL * 2, self.y +
                                 1, Direction.EAST, self.obstacle_id, SCREENSHOT_COST))
                # Or (x - 4, y - 1)
                if is_valid(self.x - 2 - EXPANDED_CELL * 2, self.y - 1):
                    cells.append(CellState(self.x - 2 - EXPANDED_CELL * 2, self.y -
                                 1, Direction.EAST, self.obstacle_id, SCREENSHOT_COST))

        return cells


class Grid:
    def __init__(self, size_x: int, size_y: int):
        self.size_x = size_x
        self.size_y = size_y
        self.obstacles: List[Obstacle] = []

    def add_obstacle(self, obstacle: Obstacle):
        # Loop through the existing obstacles to check for duplicates
        to_add = True
        for ob in self.obstacles:
            if ob == obstacle:
                to_add = False
                break

        if to_add:
            self.obstacles.append(obstacle)

    def reset_obstacles(self):
        self.obstacles = []

    def get_obstacles(self):
        return self.obstacles

    def reachable(self, x: int, y: int, turn=False, preTurn=False) -> bool:
        # Checks whether the given x,y coordinate is reachable/safe. Criterion is as such:
        # - Must be at least 4 units away in total (x+y) from the obstacle
        # - Greater distance (x or y distance) must be at least 3 units away from obstacle
        
        if not self.is_valid_coord(x, y):
            return False

        for ob in self.obstacles:
            if ob.x == 4 and ob.y <= 4 and x < 4 and y < 4:
                continue

            # Must be at least 4 units away in total (x+y)
            if abs(ob.x - x) + abs(ob.y - y) >= 4:
                continue

            if turn or preTurn:
                if max(abs(ob.x - x), abs(ob.y - y)) < EXPANDED_CELL * 2 + 1:
                    return False

            else:
                if max(abs(ob.x - x), abs(ob.y - y)) < 2:
                    return False

        return True

    def is_valid_coord(self, x: int, y: int) -> bool:
        # Checks if given position is within bounds
        if x < 1 or x >= self.size_x - 1 or y < 1 or y >= self.size_y - 1:
            return False

        return True

    def is_valid_cell_state(self, state: CellState) -> bool:
        # Checks if given state is within bounds
        return self.is_valid_coord(state.x, state.y)

    def get_view_obstacle_positions(self, retrying) -> List[List[CellState]]:
        optimal_positions = []
        for obstacle in self.obstacles:
            if obstacle.direction == 8:
                continue
            else:
                view_states = [view_state for view_state in obstacle.get_view_state(
                    retrying) if self.reachable(view_state.x, view_state.y)]
            optimal_positions.append(view_states)

        return optimal_positions