from constants import WIDTH, HEIGHT, Direction


def is_valid(center_x: int, center_y: int):
    return center_x > 0 and center_y > 0 and center_x < WIDTH - 1 and center_y < HEIGHT - 1


def command_generator(states, obstacles):
    # This function takes in a list of states and generates a list of commands for the robot to follow

    # Convert the list of obstacles into a dictionary with key as the obstacle id and value as the obstacle
    obstacles_dict = {ob['id']: ob for ob in obstacles}
    
    # Initialize commands list
    commands = []

    # Iterate through each state in the list of states
    for i in range(1, len(states)):
        steps = "000"

        # If previous state and current state are the same direction,
        if states[i].direction == states[i - 1].direction:
            # Forward - Must be (east facing AND x value increased) OR (north facing AND y value increased)
            if (states[i].x > states[i - 1].x and states[i].direction == Direction.EAST) or (
                    states[i].y > states[i - 1].y and states[i].direction == Direction.NORTH):
                commands.append("SF010")
            # Forward - Must be (west facing AND x value decreased) OR (south facing AND y value decreased)
            elif (states[i].x < states[i-1].x and states[i].direction == Direction.WEST) or (
                    states[i].y < states[i-1].y and states[i].direction == Direction.SOUTH):
                commands.append("SF010")
            # Backward - All other cases where the previous and current state is the same direction
            else:
                commands.append("SB010")

            # If any of these states has a valid screenshot ID, then add a CAP command as well to take a picture
            if states[i].screenshot_id != -1:
                # NORTH = 0
                # EAST = 2
                # SOUTH = 4
                # WEST = 6

                current_ob_dict = obstacles_dict[states[i].screenshot_id] # {'x': 9, 'y': 10, 'd': 6, 'id': 9}
                current_robot_position = states[i] # {'x': 1, 'y': 8, 'd': <Direction.NORTH: 0>, 's': -1}

                # Obstacle facing WEST, robot facing EAST
                if current_ob_dict['d'] == 6 and current_robot_position.direction == 2:
                    if current_ob_dict['y'] > current_robot_position.y:
                        commands.append(f"CAP{states[i].screenshot_id}_L")
                    elif current_ob_dict['y'] == current_robot_position.y:
                        commands.append(f"CAP{states[i].screenshot_id}_C")
                    elif current_ob_dict['y'] < current_robot_position.y:
                        commands.append(f"CAP{states[i].screenshot_id}_R")
                    else:
                        commands.append(f"CAP{states[i].screenshot_id}")
                
                # Obstacle facing EAST, robot facing WEST
                elif current_ob_dict['d'] == 2 and current_robot_position.direction == 6:
                    if current_ob_dict['y'] > current_robot_position.y:
                        commands.append(f"CAP{states[i].screenshot_id}_R")
                    elif current_ob_dict['y'] == current_robot_position.y:
                        commands.append(f"CAP{states[i].screenshot_id}_C")
                    elif current_ob_dict['y'] < current_robot_position.y:
                        commands.append(f"CAP{states[i].screenshot_id}_L")
                    else:
                        commands.append(f"CAP{states[i].screenshot_id}")

                # Obstacle facing NORTH, robot facing SOUTH
                elif current_ob_dict['d'] == 0 and current_robot_position.direction == 4:
                    if current_ob_dict['x'] > current_robot_position.x:
                        commands.append(f"CAP{states[i].screenshot_id}_L")
                    elif current_ob_dict['x'] == current_robot_position.x:
                        commands.append(f"CAP{states[i].screenshot_id}_C")
                    elif current_ob_dict['x'] < current_robot_position.x:
                        commands.append(f"CAP{states[i].screenshot_id}_R")
                    else:
                        commands.append(f"CAP{states[i].screenshot_id}")

                # Obstacle facing SOUTH, robot facing NORTH
                elif current_ob_dict['d'] == 4 and current_robot_position.direction == 0:
                    if current_ob_dict['x'] > current_robot_position.x:
                        commands.append(f"CAP{states[i].screenshot_id}_R")
                    elif current_ob_dict['x'] == current_robot_position.x:
                        commands.append(f"CAP{states[i].screenshot_id}_C")
                    elif current_ob_dict['x'] < current_robot_position.x:
                        commands.append(f"CAP{states[i].screenshot_id}_L")
                    else:
                        commands.append(f"CAP{states[i].screenshot_id}")
            continue

        # If previous state and current state are not the same direction, it means that there will be a turn command involved
        # Assume there are 4 turning command: RF, LF, LB, RB (the turn command will turn the robot 90 degrees)
        # RF00 | RF30: Forward Right;
        # LF00 | LF30: Forward Left;
        # RB00 | RB30: Backward Right;
        # LB00 | LB30: Backward Left;

        # Facing north previously
        if states[i - 1].direction == Direction.NORTH:
            # Facing east afterwards
            if states[i].direction == Direction.EAST:
                # y value increased -> Forward Right
                if states[i].y > states[i - 1].y:
                    commands.append("RF090")
                # y value decreased -> Backward Left
                else:
                    commands.append("LB090")
            # Facing west afterwards
            elif states[i].direction == Direction.WEST:
                # y value increased -> Forward Left
                if states[i].y > states[i - 1].y:
                    commands.append("LF090")
                # y value decreased -> Backward Right
                else:
                    commands.append("RB090")
            else:
                raise Exception("Invalid turning direction")

        elif states[i - 1].direction == Direction.EAST:
            if states[i].direction == Direction.NORTH:
                if states[i].y > states[i - 1].y:
                    commands.append("LF090")
                else:
                    commands.append("RB090")

            elif states[i].direction == Direction.SOUTH:
                if states[i].y > states[i - 1].y:
                    commands.append("LB090")
                else:
                    commands.append("RF090")
            else:
                raise Exception("Invalid turning direction")

        elif states[i - 1].direction == Direction.SOUTH:
            if states[i].direction == Direction.EAST:
                if states[i].y > states[i - 1].y:
                    commands.append("RB090")
                else:
                    commands.append("LF090")
            elif states[i].direction == Direction.WEST:
                if states[i].y > states[i - 1].y:
                    commands.append("LB090")
                else:
                    commands.append("RF090")
            else:
                raise Exception("Invalid turning direction")

        elif states[i - 1].direction == Direction.WEST:
            if states[i].direction == Direction.NORTH:
                if states[i].y > states[i - 1].y:
                    commands.append("RF090")
                else:
                    commands.append("LB090")
            elif states[i].direction == Direction.SOUTH:
                if states[i].y > states[i - 1].y:
                    commands.append("RB090")
                else:
                    commands.append("LF090")
            else:
                raise Exception("Invalid turning direction")
        else:
            raise Exception("Invalid position")

        # If any of these states has a valid screenshot ID, then add a CAP command as well to take a picture
        if states[i].screenshot_id != -1:  
            # NORTH = 0
            # EAST = 2
            # SOUTH = 4
            # WEST = 6

            current_ob_dict = obstacles_dict[states[i].screenshot_id] 
            current_robot_position = states[i] 

            # Obstacle facing WEST, robot facing EAST
            if current_ob_dict['d'] == 6 and current_robot_position.direction == 2:
                if current_ob_dict['y'] > current_robot_position.y:
                    commands.append(f"CAP{states[i].screenshot_id}_L")
                elif current_ob_dict['y'] == current_robot_position.y:
                    commands.append(f"CAP{states[i].screenshot_id}_C")
                elif current_ob_dict['y'] < current_robot_position.y:
                    commands.append(f"CAP{states[i].screenshot_id}_R")
                else:
                    commands.append(f"CAP{states[i].screenshot_id}")
            
            # Obstacle facing EAST, robot facing WEST
            elif current_ob_dict['d'] == 2 and current_robot_position.direction == 6:
                if current_ob_dict['y'] > current_robot_position.y:
                    commands.append(f"CAP{states[i].screenshot_id}_R")
                elif current_ob_dict['y'] == current_robot_position.y:
                    commands.append(f"CAP{states[i].screenshot_id}_C")
                elif current_ob_dict['y'] < current_robot_position.y:
                    commands.append(f"CAP{states[i].screenshot_id}_L")
                else:
                    commands.append(f"CAP{states[i].screenshot_id}")

            # Obstacle facing NORTH, robot facing SOUTH
            elif current_ob_dict['d'] == 0 and current_robot_position.direction == 4:
                if current_ob_dict['x'] > current_robot_position.x:
                    commands.append(f"CAP{states[i].screenshot_id}_L")
                elif current_ob_dict['x'] == current_robot_position.x:
                    commands.append(f"CAP{states[i].screenshot_id}_C")
                elif current_ob_dict['x'] < current_robot_position.x:
                    commands.append(f"CAP{states[i].screenshot_id}_R")
                else:
                    commands.append(f"CAP{states[i].screenshot_id}")

            # Obstacle facing SOUTH, robot facing NORTH
            elif current_ob_dict['d'] == 4 and current_robot_position.direction == 0:
                if current_ob_dict['x'] > current_robot_position.x:
                    commands.append(f"CAP{states[i].screenshot_id}_R")
                elif current_ob_dict['x'] == current_robot_position.x:
                    commands.append(f"CAP{states[i].screenshot_id}_C")
                elif current_ob_dict['x'] < current_robot_position.x:
                    commands.append(f"CAP{states[i].screenshot_id}_L")
                else:
                    commands.append(f"CAP{states[i].screenshot_id}")

    # Final command is the stop command (FIN)
    commands.append("FIN")  

    # Compress commands if there are consecutive forward or backward commands
    compressed_commands = [commands[0]]

    for i in range(1, len(commands)):
        # If both commands are SB
        if commands[i].startswith("SB") and compressed_commands[-1].startswith("SB"):
            # Get the number of steps of previous command
            if int(compressed_commands[-1][2]) == 0:
                steps = int(compressed_commands[-1][3:])
            else:
                steps = int(compressed_commands[-1][2:])

            steps += 10
            if steps < 100:
                compressed_commands[-1] = "SB0{}".format(steps)
                continue
            else:
                compressed_commands[-1] = "SB{}".format(steps)
                continue

        # If both commands are SF
        elif commands[i].startswith("SF") and compressed_commands[-1].startswith("SF"):
            # Get the number of steps of previous command
            if int(compressed_commands[-1][2]) == 0:
                steps = int(compressed_commands[-1][3:])
            else:
                steps = int(compressed_commands[-1][2:])

            steps += 10
            if steps < 100:
                compressed_commands[-1] = "SF0{}".format(steps)
                continue
            else:
                compressed_commands[-1] = "SF{}".format(steps)
                continue
        
        # Otherwise, just add as usual
        compressed_commands.append(commands[i])

    return compressed_commands