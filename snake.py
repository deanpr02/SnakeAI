import pygame
import math
import random


SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720
STARTING_POS = (SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
RIGHT_BOUNDARY = 720
LEFT_BOUNDARY = 0
TOP_BOUNDARY = 0
BOTTOM_BOUNDARY = 720
PLAYER_WIDTH = 16
PLAYER_HEIGHT = 16
PLAYER_SPEED = 2
DIR_DICT = {"LEFT": (-PLAYER_SPEED,0),"RIGHT":(PLAYER_SPEED,0),"UP":(0,-PLAYER_SPEED),"DOWN":(0,PLAYER_SPEED)}
GEN = 0

#TODO:
#1. Have AI learn to not run into its tail
#2. Save the best snake
#3. Be able to load the best snake

class SnakePart:
    def __init__(self, body,current_direction):
        #This will be a queue of what each snake body part needs to follow
        self.direction_queue = []
        #This will be the positions of which to enact the directions for each snake body part
        self.position_queue = []
        #body will be type pygame.rect which will store the rect object of the Snake Part
        self.body = body
        self.current_position = (body.x,body.y)
        self.current_direction = current_direction

    #This should move the snake part in its current direction until it reaches the point
    #Where it should change directions, then its direction would change and it would
    #Pop the lists of directions and positions to get to the next one

    #def move_part(self):
        #self.body.move_ip(self.current_direction[0],self.current_direction[1])
        #self.current_position = (self.body.x,self.body.y)
        #if(len(self.direction_queue) > 0):
            #if(self.current_position == self.position_queue[0]):
                #self.current_direction = self.direction_queue.pop(0)
                #self.position_queue.pop(0)
    

    def move_part(self):
        new_x = self.body.x + self.current_direction[0]
        new_y = self.body.y + self.current_direction[1]

        # Check if the new position is within the screen bounds
        if 0 <= new_x < SCREEN_WIDTH and 0 <= new_y < SCREEN_HEIGHT:
            self.body.move_ip(self.current_direction[0], self.current_direction[1])
            self.current_position = (self.body.x, self.body.y)

            # Check if the direction and position queues are synchronized
            if len(self.direction_queue) == len(self.position_queue) and len(self.direction_queue) > 0:
                if self.current_position == self.position_queue[0]:
                    self.current_direction = self.direction_queue.pop(0)
                    self.position_queue.pop(0)
                #else:
                #    print(len(self.direction_queue))
                #    print(len(self.position_queue))
                #    print("Error: Direction and position queues are out of sync")

        return None
#Snake Class: controls the entire snake and holds the data which references the list of snake parts
class Snake:
    def __init__(self, screen):
        self.head = pygame.Rect(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        self.current_position = (self.head.x,self.head.y)
        self.previous_position = (0,0)
        self.current_direction = (0,0)
        self.hit_box = pygame.Rect(0,0,2,2)
        self.spawned = False
        self.coin = pygame.Rect(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        self.coin_location = (self.coin.x,self.coin.y)
        self.current_distance = -1
        self.previous_distance = 9999
        self.best_distance = 9999
        self.prev_moves = []
        self.x_bounds = [self.head.x,self.head.x]
        self.y_bounds = [self.head.y,self.head.y]
        self.snake_part_list = []
        self.time_last_collected = 0
        self.start_time = 0
        self.timer = 0
        self.timer_started = False
        self.next_phase = False

    
    
    #This will trigger when we go over a coin
    def add_snake_part(self):
        new_part = pygame.Rect(self.current_position[0],self.current_position[1],PLAYER_WIDTH,PLAYER_WIDTH)
        last_snake_item = pygame.Rect(self.head.x,self.head.y,PLAYER_WIDTH,PLAYER_WIDTH)
        last_snake_item_direction = self.current_direction
        inherit_directions = []
        inherit_positions = []

        #If the length of our snake is more than one we will want to have the new snake part inherit the back of the snakes attributes so it follows the correct pattern
        if(len(self.snake_part_list) > 0):
            new_part.x = self.snake_part_list[-1].body.x
            new_part.y = self.snake_part_list[-1].body.y
            last_snake_item = self.snake_part_list[-1].body
            inherit_directions = self.snake_part_list[-1].direction_queue[::]
            inherit_positions = self.snake_part_list[-1].position_queue[::]
            last_snake_item_direction = self.snake_part_list[-1].current_direction
        
        #Checks to see what the direction of the last snake_part is so we can correctly orientate the newly added snake_part
        if(last_snake_item_direction == (0,-PLAYER_SPEED)):
            new_part.top = last_snake_item.bottom
            new_part.y += 2
        if(last_snake_item_direction == (0,PLAYER_SPEED)):
            new_part.bottom = last_snake_item.top
            new_part.y -= 2
        if(last_snake_item_direction == (-PLAYER_SPEED,0)):
            new_part.left = last_snake_item.right
            new_part.x += 2
        if(last_snake_item_direction == (PLAYER_SPEED,0)):
            new_part.right = last_snake_item.left
            new_part.x -= 2

        new_snake_part = SnakePart(new_part,last_snake_item_direction)
        new_snake_part.direction_queue = inherit_directions
        new_snake_part.position_queue = inherit_positions
        self.snake_part_list.append(new_snake_part)

        
    def queue_directions(self, direction):
        for snake_part in self.snake_part_list:
            #So now every snake part will have a queue of directions and a queue of when they
            #Should execute those direction changes.
            snake_part.direction_queue.append(direction)
            snake_part.position_queue.append(self.current_position)

    def move_snake_parts(self):
        for snake_part in self.snake_part_list:
            snake_part.move_part()
            #set our bounds for the snake
            if(snake_part.body.x < self.head.x and snake_part.body.x < self.x_bounds[0]):
                self.x_bounds[0] = snake_part.body.x
            if(snake_part.body.x > self.head.x and snake_part.body.x > self.x_bounds[1]):
                self.x_bounds[1] = snake_part.body.x
            if(snake_part.body.y < self.head.y and snake_part.body.y < self.y_bounds[0]):
                self.y_bounds[0] = snake_part.body.y
            if(snake_part.body.y > self.head.y and snake_part.body.y > self.y_bounds[1]):
                self.y_bounds[1] = snake_part.body.y



    
    def draw_snake(self,screen):
        outline = pygame.Rect(self.head.x-1,self.head.y-1,PLAYER_WIDTH+2,PLAYER_HEIGHT+2)
        pygame.draw.rect(screen,"white",outline,PLAYER_WIDTH+2)
        pygame.draw.rect(screen,"red",self.head,PLAYER_WIDTH)
        for snake_part in self.snake_part_list:
            outline = pygame.Rect(snake_part.body.x-1,snake_part.body.y-1,PLAYER_WIDTH+2,PLAYER_HEIGHT+2)
            pygame.draw.rect(screen,"white",outline,PLAYER_WIDTH+2)
            pygame.draw.rect(screen,"red",snake_part.body,PLAYER_WIDTH)
    


    def move_left(self):
        self.current_direction = DIR_DICT["LEFT"]
        self.queue_directions(DIR_DICT["LEFT"])
        self.previous_position = self.current_position
        self.head.move_ip(-PLAYER_SPEED,0)
        self.current_position = (self.head.x,self.head.y)
        self.hit_box.update(self.head.x+(PLAYER_WIDTH/2-1),self.head.y+(PLAYER_HEIGHT/2-1),2,2)
        self.prev_moves.append(self.previous_position)
        self.move_snake_parts()

    def move_right(self):
        self.current_direction = DIR_DICT["RIGHT"]
        self.queue_directions(DIR_DICT["RIGHT"])
        self.previous_position = self.current_position
        self.head.move_ip(PLAYER_SPEED,0)
        self.current_position = (self.head.x,self.head.y)
        self.hit_box.update(self.head.x+(PLAYER_WIDTH/2-1),self.head.y+(PLAYER_HEIGHT/2-1),2,2)
        self.prev_moves.append(self.previous_position)
        self.move_snake_parts()
    
    
    def move_up(self):
        self.current_direction = DIR_DICT["UP"]
        self.queue_directions(DIR_DICT["UP"])
        self.previous_position = self.current_position
        self.head.move_ip(0,-PLAYER_SPEED)
        self.current_position = (self.head.x,self.head.y)
        self.hit_box.update(self.head.x+(PLAYER_WIDTH/2-1),self.head.y+(PLAYER_HEIGHT/2-1),2,2)
        self.prev_moves.append(self.previous_position)
        self.move_snake_parts()

    def move_down(self):
        self.current_direction = DIR_DICT["DOWN"]
        self.queue_directions(DIR_DICT["DOWN"])
        self.previous_position = self.current_position
        self.head.move_ip(0,PLAYER_SPEED)
        self.current_position = (self.head.x,self.head.y)
        self.hit_box.update(self.head.x+(PLAYER_WIDTH/2-1),self.head.y+(PLAYER_HEIGHT/2-1),2,2)
        self.prev_moves.append(self.previous_position)
        self.move_snake_parts()

    def check_for_collision(self):
        snake_part_rects = [rect.body for rect in self.snake_part_list]
        if(self.hit_box.collideobjects(snake_part_rects)):
            self.head.update(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
            self.reset_snake()
            return True
        return False
    
    def reset_snake(self):
        self.snake_part_list.clear()
        self.head.update(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        self.current_position = (0,0)
        self.previous_position = (0,0)
        #self.prev_moves.clear()

    #I think for each snake we will want it to have its own personal coin to get track of
    def spawn_coin(self):
        if not self.spawned:
            if self.current_direction == DIR_DICT["LEFT"]:
                self.coin.update(random.randint(self.head.x + PLAYER_WIDTH, SCREEN_WIDTH)-PLAYER_WIDTH, random.randint(0, SCREEN_HEIGHT - PLAYER_HEIGHT),PLAYER_WIDTH,PLAYER_HEIGHT)
                self.coin_location = (self.coin.x, self.coin.y)
                self.spawned = True
            elif self.current_direction == DIR_DICT["RIGHT"]:
                self.coin.update(random.randint(PLAYER_WIDTH, self.head.x+PLAYER_WIDTH)-PLAYER_WIDTH, random.randint(0, SCREEN_HEIGHT - PLAYER_HEIGHT),PLAYER_WIDTH,PLAYER_HEIGHT)
                self.coin_location = (self.coin.x, self.coin.y)
                self.spawned = True
            elif self.current_direction == DIR_DICT["UP"]:
                self.coin.update(random.randint(0, SCREEN_WIDTH - PLAYER_WIDTH), random.randint(self.head.y + PLAYER_HEIGHT, SCREEN_HEIGHT)-PLAYER_HEIGHT,PLAYER_WIDTH,PLAYER_HEIGHT)
                self.coin_location = (self.coin.x, self.coin.y)
                self.spawned = True
            elif self.current_direction == DIR_DICT["DOWN"]:
                self.coin.update(random.randint(0, SCREEN_WIDTH - PLAYER_WIDTH), random.randint(PLAYER_HEIGHT, self.head.y + PLAYER_HEIGHT)-PLAYER_HEIGHT,PLAYER_WIDTH,PLAYER_HEIGHT)
                self.coin_location = (self.coin.x, self.coin.y)
                self.spawned = True
            else:
                self.coin.update(random.random()*(SCREEN_WIDTH-20),random.random()*(SCREEN_HEIGHT-20),PLAYER_WIDTH,PLAYER_HEIGHT)
                self.coin_location = (self.coin.x,self.coin.y)
                self.spawned = True
        #if(not self.spawned):
            #self.coin.update(random.random()*(SCREEN_WIDTH-20),random.random()*(SCREEN_HEIGHT-20),PLAYER_WIDTH,PLAYER_HEIGHT)
            #self.coin_location = (self.coin.x,self.coin.y)
            #self.spawned = True
    
    def draw_coin(self,screen):
        pygame.draw.rect(screen,"yellow",self.coin,PLAYER_WIDTH)

    def calc_distance(self):
        x_dist = self.head.x - self.coin.x
        x_dist = x_dist**2
        y_dist = self.head.y - self.coin.y
        y_dist = y_dist**2
        distance = math.sqrt(x_dist+y_dist)
        return distance
    
    def distance(self,point,snake_part):
        x_dist = (point[0] - snake_part.body.x)
        x_dist *= x_dist
        y_dist = (point[1] - snake_part.body.y)
        y_dist *= y_dist
        return math.sqrt(x_dist+y_dist)
    
    def check_if_inbounds(self):
        if(self.head.right >= RIGHT_BOUNDARY):
            return True
        if(self.head.top <= TOP_BOUNDARY):
            return True
        if(self.head.left <= LEFT_BOUNDARY):
            return True
        if(self.head.bottom >= BOTTOM_BOUNDARY):
            return True
        self.current_position = (self.head.x,self.head.y)
        return False
    
    """
    def check_if_obstacles(self):
        obstacles = [True,True,True,True]
        for snake_part in self.snake_part_list:
            if snake_part.body.x < self.head.x and snake_part.body.x <= self.head.x+PLAYER_WIDTH/2 and snake_part.body.x >= self.head.x-PLAYER_WIDTH/2:
                obstacles[0] = False
            if snake_part.body.x > self.head.x and snake_part.body.x <= self.head.x+PLAYER_WIDTH/2 and snake_part.body.x >= self.head.x-PLAYER_WIDTH/2:
                obstacles[1] = False
            if snake_part.body.y < self.head.y and snake_part.body.y <= self.head.y+PLAYER_HEIGHT/2 and snake_part.body.y >= self.head.y-PLAYER_HEIGHT/2:
                obstacles[2] = False
            if snake_part.body.y > self.head.y and snake_part.body.y <= self.head.y+PLAYER_HEIGHT/2 and snake_part.body.y >= self.head.y-PLAYER_HEIGHT/2:
                obstacles[3] = False
        return obstacles
    """

    #flip flopped the head and body, could change back(shouldnt matter)
    def check_if_obstacles(self):
        obstacles = [True,True,True,True]
        for snake_part in self.snake_part_list:
            #left
            if self.head.x < snake_part.body.x and self.head.y <= snake_part.body.y+PLAYER_HEIGHT and self.head.y >= snake_part.body.y-PLAYER_HEIGHT:
                obstacles[1] = False
            #right
            if self.head.x > snake_part.body.x and self.head.y <= snake_part.body.y+PLAYER_HEIGHT and self.head.y >= snake_part.body.y-PLAYER_HEIGHT:
                obstacles[0] = False
            if self.head.y < snake_part.body.y and self.head.x <= snake_part.body.x+PLAYER_WIDTH and self.head.x >= snake_part.body.x-PLAYER_WIDTH:
                obstacles[3] = False
            if self.head.y > snake_part.body.y and self.head.x <= snake_part.body.x+PLAYER_WIDTH and self.head.x >= snake_part.body.x-PLAYER_WIDTH:
                obstacles[2] = False
        return obstacles


    def calc_distance_to_nearest_part(self):
        x,y = self.head.x,self.head.y
        left_move = (x + DIR_DICT["LEFT"][0],y)
        right_move = (x + DIR_DICT["RIGHT"][0],y)
        up_move = (x,y + DIR_DICT["UP"][1])
        down_move = (x,y + DIR_DICT["DOWN"][1])
        distances = [1000,1000,1000,1000]

        for part in self.snake_part_list:
            if part.body.x < x:
                distance = self.distance(left_move,part)
                if distance < distances[0]:
                    distances[0] = distance
            elif part.body.x > x:
                distance = self.distance(right_move,part)
                if distance < distances[1]:
                    distances[1] = distance
            if part.body.y < y:
                distance = self.distance(up_move,part)
                if distance < distances[2]:
                    distances[2] = distance
            elif part.body.y > y:
                distance = self.distance(down_move,part)
                if distance < distances[3]:
                    distances[3] = distance
        return distances


    """
    def calc_distance_to_nearest_part(self):
        x, y = self.head.x, self.head.y
        # LEFT, RIGHT, UP, DOWN
        distances = [x-LEFT_BOUNDARY, RIGHT_BOUNDARY-x, y-TOP_BOUNDARY, BOTTOM_BOUNDARY-y]
        if len(self.snake_part_list) <= 1:
            return distances

        for part in self.snake_part_list[1:]:
            part_x, part_y = part.body.x, part.body.y
            x_dist = abs(part_x - x)
            y_dist = abs(part_y - y)

            if part_x < x and x_dist < distances[0]:
                distances[0] = x_dist
            elif part_x > x and x_dist < distances[1]:
                distances[1] = x_dist

            if part_y < y and y_dist < distances[2]:
                distances[2] = y_dist
            elif part_y > y and y_dist < distances[3]:
                distances[3] = y_dist

        return distances
    """
    
    def calc_bound_distances(self):
        left_bound_d = abs(LEFT_BOUNDARY - self.head.x)
        right_bound_d = abs(RIGHT_BOUNDARY - self.head.x)
        top_bound_d = abs(TOP_BOUNDARY - self.head.y)
        bot_bound_d = abs(BOTTOM_BOUNDARY - self.head.y)
        bound_distances = [left_bound_d,right_bound_d,top_bound_d,bot_bound_d]
        return bound_distances
    
    def calc_input_distances(self,x_inputs,y_inputs):
        for i, x_input in enumerate(x_inputs):
            disp = self.coin.x - x_input
            x_inputs[i] = disp

        for i, y_input in enumerate(y_inputs):
            disp = self.coin.y - y_input
            y_inputs[i] = disp

        return x_inputs,y_inputs
    
    def calc_inputs(self):
        x_left = self.head.x + DIR_DICT["LEFT"][0]
        x_right = self.head.x + DIR_DICT["RIGHT"][0]
        x_up = self.head.x + DIR_DICT["UP"][0]
        x_down = self.head.x + DIR_DICT["DOWN"][0]
        x_inputs = [x_left,x_right,x_up,x_down]
        y_left = self.head.y + DIR_DICT["LEFT"][1]
        y_right = self.head.y + DIR_DICT["RIGHT"][1]
        y_up = self.head.y + DIR_DICT["UP"][1]
        y_down = self.head.y + DIR_DICT["DOWN"][1]
        y_inputs = [y_left,y_right,y_up,y_down]
        return x_inputs,y_inputs
    