''' THIS REPRESENTS A FILE THAT WILL BE USED TO LOAD IN THE TRAINED NEURAL NETWORK SNAKE TO SEE HOW IT OPERATES AFTER IT IS SAVED SO WE DO NOT HAVE TO RETRAIN THE AI EVERY TIME WE RUN THE PROGRAM.'''

import pygame
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


#TODO:
#Organize the code better
#Execute death sequence when snake_head intersects with any part of the snake
#Add a scoring element which will count up when the player collects a coin
#Fix bug where coins spawn too far on the sides so they are barely visible
#We need to smooth the movement so you cant make sudden adjustments which will cause snake to go off course because it cannot adjust that quickly. Additionally, we need to make the movement stick to squares so
#We dont go in between squares this will make the movement look smoother and hopefully work good by implementing delays so you can not adjust movement too quickly, but making it easier to align with the coins.
#Snake Part class: controls individual snake parts that are added to the snake as the player progresses
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
    def move_part(self):
        self.body.move_ip(self.current_direction[0],self.current_direction[1])
        self.current_position = (self.body.x,self.body.y)
        if(len(self.direction_queue) > 0):
            if(self.current_position == self.position_queue[0]):
                self.current_direction = self.direction_queue.pop(0)
                self.position_queue.pop(0)

#Snake Class: controls the entire snake and holds the data which references the list of snake parts
class Snake:
    def __init__(self, screen):
        self.head = pygame.Rect(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        self.current_position = (0,0)
        self.current_direction = (0,0)
        self.hit_box = pygame.Rect(0,0,2,2)
        self.spawned = False
        self.coin = pygame.Rect(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        self.coin_location = (self.coin.x,self.coin.y)
        #We will want this because it will allow us to add a snake part to the end of the snake
        #Each snake part will could have its own direction so we will have an attribute in the
        #SnakePart class that will have its current direction, then based on this we can
        #Add a particular snake part in a certain position.
        self.snake_part_list = []

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
        self.head.move_ip(-PLAYER_SPEED,0)
        self.current_position = (self.head.x,self.head.y)
        self.hit_box.update(self.head.x+(PLAYER_WIDTH/2-1),self.head.y+(PLAYER_HEIGHT/2-1),2,2)
        self.move_snake_parts()

    def move_right(self):
        self.current_direction = DIR_DICT["RIGHT"]
        self.queue_directions(DIR_DICT["RIGHT"])
        self.head.move_ip(PLAYER_SPEED,0)
        self.current_position = (self.head.x,self.head.y)
        self.hit_box.update(self.head.x+(PLAYER_WIDTH/2-1),self.head.y+(PLAYER_HEIGHT/2-1),2,2)
        self.move_snake_parts()
    
    def move_up(self):
        self.current_direction = DIR_DICT["UP"]
        self.queue_directions(DIR_DICT["UP"])
        self.head.move_ip(0,-PLAYER_SPEED)
        self.current_position = (self.head.x,self.head.y)
        self.hit_box.update(self.head.x+(PLAYER_WIDTH/2-1),self.head.y+(PLAYER_HEIGHT/2-1),2,2)
        self.move_snake_parts()

    def move_down(self):
        self.current_direction = DIR_DICT["DOWN"]
        self.queue_directions(DIR_DICT["DOWN"])
        self.head.move_ip(0,PLAYER_SPEED)
        self.current_position = (self.head.x,self.head.y)
        self.hit_box.update(self.head.x+(PLAYER_WIDTH/2-1),self.head.y+(PLAYER_HEIGHT/2-1),2,2)
        self.move_snake_parts()

    def check_for_collision(self):
        snake_part_rects = [rect.body for rect in self.snake_part_list]
        if(self.hit_box.collideobjects(snake_part_rects)):
            self.head.update(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
            self.reset_snake()
    
    def reset_snake(self):
        self.snake_part_list.clear()
        self.head.update(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        self.current_position = 0

    #I think for each snake we will want it to have its own personal coin to get track of
    def spawn_coin(self):
        if(not self.spawned):
            self.coin.update(random.random()*(SCREEN_WIDTH-20),random.random()*(SCREEN_HEIGHT-20),PLAYER_WIDTH,PLAYER_HEIGHT)
            self.coin_location = (self.coin.x,self.coin.y)
            self.spawned = True
    
    def draw_coin(self,screen):
        pygame.draw.rect(screen,"yellow",self.coin,PLAYER_WIDTH)





#Game-Specific Functions
def manage_player_movement(snake):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        snake.move_up()
    elif keys[pygame.K_s]:
        snake.move_down()
    elif keys[pygame.K_a]:
        snake.move_left()
    elif keys[pygame.K_d]:
        snake.move_right()

def check_if_inbounds(snake):
    if(snake.head.right == RIGHT_BOUNDARY):
        snake.head.update(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        snake.reset_snake()
        return
    if(snake.head.top == TOP_BOUNDARY):
        snake.head.update(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        snake.reset_snake()
        return
    if(snake.head.left == LEFT_BOUNDARY):
        snake.head.update(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        snake.reset_snake()
        return
    if(snake.head.bottom == BOTTOM_BOUNDARY):
        snake.head.update(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        snake.reset_snake()
        return
    snake.current_position = (snake.head.x,snake.head.y)


pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
clock = pygame.time.Clock()
my_font = pygame.font.SysFont('Comic Sans MS',20)

running = True
movement_dir = ""
collected = False
#dir_dict = {"LEFT": (-2,0),"RIGHT":(2,0),"UP":(0,-2),"DOWN":(0,2)}

#This is the class that references the entire Snake class which will be composed
#of a bunch of snake parts
snake = Snake(screen)
#This represents the head of the snake which will be responding to player input controls
#Represents the item which will grow the snake
item_to_collect = pygame.Rect(STARTING_POS[0], STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
#Outline around snake_head to make it more defined looking
#outline = pygame.Rect(starting_pos.x-2,starting_pos.y-2,PLAYER_WIDTH+2,PLAYER_HEIGHT+2)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
    
    #fill screen with a color
    screen.fill("black")
    text_surface = my_font.render(f"Score: {len(snake.snake_part_list)}",False,"white")
    screen.blit(text_surface,(0,0))

    #If a coin is not currently spawned for a snake, then spawn the coin
    
    snake.spawn_coin()
    snake.draw_coin(screen)

    #Checks to see if a item has been collected; if it has then add a snake and allow for a new item to be spawned in
    if(snake.head.colliderect(snake.coin)):
        snake.spawned = False
        snake.add_snake_part()

    #DRAW RECTS

    #Have a method for drawing the snake
         
    #FUNCTION CALLS
    

    #This creates constant movement in a direction once a WASD key has been pushed; direction
    # will not change until a different WASD key has been pushed. 
    
    manage_player_movement(snake)
    snake.draw_snake(screen)
    snake.check_for_collision()
    check_if_inbounds(snake)


    #show display to the screen
    pygame.display.flip()
    dt = clock.tick(60) / 1000


#OUR OLD SNAKE MODEL FILE
''' THIS WILL BE THE FILE THAT LOADS ALL THE SNAKE GENOMES INTO IT SO IT WILL BE MODIFIED TO HOUSE MULTIPLE SNAKES'''

import pygame
import random
import neat
import os
import math
pygame.font.init()


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
STAT_FONT = pygame.font.SysFont("comicsans", 50)

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
            else:
                print("Error: Direction and position queues are out of sync")

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
        if(not self.spawned):
            self.coin.update(random.random()*(SCREEN_WIDTH-20),random.random()*(SCREEN_HEIGHT-20),PLAYER_WIDTH,PLAYER_HEIGHT)
            self.coin_location = (self.coin.x,self.coin.y)
            self.spawned = True
    
    def draw_coin(self,screen):
        pygame.draw.rect(screen,"yellow",self.coin,PLAYER_WIDTH)

    def calc_distance(self):
        x_dist = self.head.x - self.coin.x
        x_dist = x_dist**2
        y_dist = self.head.y - self.coin.y
        y_dist = y_dist**2
        distance = math.sqrt(x_dist+y_dist)
        return distance
    






#Game-Specific Functions
def manage_player_movement(snake):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        snake.move_up()
    elif keys[pygame.K_s]:
        snake.move_down()
    elif keys[pygame.K_a]:
        snake.move_left()
    elif keys[pygame.K_d]:
        snake.move_right()

def check_if_inbounds(snake):
    if(snake.head.right >= RIGHT_BOUNDARY):
        return True
    if(snake.head.top <= TOP_BOUNDARY):
        return True
    if(snake.head.left <= LEFT_BOUNDARY):
        return True
    if(snake.head.bottom >= BOTTOM_BOUNDARY):
        return True
    snake.current_position = (snake.head.x,snake.head.y)
    return False

def calc_time(snakes):
    for snake in snakes:
        time_without_coin = pygame.time.get_ticks() - snake.start_time
        snake.end_time = time_without_coin

def calc_distance(obj1, obj2):
    x_dist = obj2[0] - obj1[0]
    x_dist = x_dist ** 2
    y_dist = obj2[1] - obj1[1]
    y_dist = y_dist ** 2
    dist = math.sqrt(x_dist,y_dist)
    return dist

def calc_inputs(snake):
    #inputs = [X_LEFT, X_RIGHT, X_UP, X_DOWN, Y_LEFT, Y_RIGHT, Y_UP, Y_DOWN]
    x_left = snake.head.x + DIR_DICT["LEFT"][0]
    x_right = snake.head.x + DIR_DICT["RIGHT"][0]
    x_up = snake.head.x + DIR_DICT["UP"][0]
    x_down = snake.head.x + DIR_DICT["DOWN"][0]
    x_inputs = [x_left,x_right,x_up,x_down]
    y_left = snake.head.y + DIR_DICT["LEFT"][1]
    y_right = snake.head.y + DIR_DICT["RIGHT"][1]
    y_up = snake.head.y + DIR_DICT["UP"][1]
    y_down = snake.head.y + DIR_DICT["DOWN"][1]
    y_inputs = [y_left,y_right,y_up,y_down]
    return x_inputs,y_inputs
            
def calc_input_distances(x_inputs,y_inputs,snake):
    for i, x_input in enumerate(x_inputs):
        disp = snake.coin.x - x_input
        x_inputs[i] = disp

    for i, y_input in enumerate(y_inputs):
        disp = snake.coin.y - y_input
        y_inputs[i] = disp
    
    return x_inputs,y_inputs

def calc_bound_distances(snake):
    left_bound_d = abs(LEFT_BOUNDARY - snake.head.x)
    right_bound_d = abs(RIGHT_BOUNDARY - snake.head.x)
    top_bound_d = abs(TOP_BOUNDARY - snake.head.y)
    bot_bound_d = abs(BOTTOM_BOUNDARY - snake.head.y)
    bound_distances = [left_bound_d,right_bound_d,top_bound_d,bot_bound_d]
    return bound_distances

def check_if_obstacles(snake):
    obstacles = [True,True,True,True]
    for snake_part in snake.snake_part_list:
        if snake_part.body.x < snake.head.x and snake_part.body.x <= snake.head.x+PLAYER_WIDTH/2 and snake_part.body.x >= snake.head.x-PLAYER_WIDTH/2:
            obstacles[0] = False
        if snake_part.body.x > snake.head.x and snake_part.body.x <= snake.head.x+PLAYER_WIDTH/2 and snake_part.body.x >= snake.head.x-PLAYER_WIDTH/2:
            obstacles[1] = False
        if snake_part.body.y < snake.head.y and snake_part.body.y <= snake.head.y+PLAYER_HEIGHT/2 and snake_part.body.y >= snake.head.y-PLAYER_HEIGHT/2:
            obstacles[2] = False
        if snake_part.body.y > snake.head.y and snake_part.body.y <= snake.head.y+PLAYER_HEIGHT/2 and snake_part.body.y >= snake.head.y-PLAYER_HEIGHT/2:
            obstacles[3] = False
    return obstacles

def calc_distance_to_nearest_part(snake):
    x, y = snake.head.x, snake.head.y
    # LEFT, RIGHT, UP, DOWN
    distances = [1000, 1000, 1000, 1000]
    if len(snake.snake_part_list) <= 1:
        return distances
    
    for part in snake.snake_part_list[1:]:
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
def calc_distance_to_nearest_part(snake):
    x, y = snake.head.x, snake.head.y
    #LEFT,RIGHT,UP,DOWN
    distances = [1000,1000,1000,1000]
    if(len(snake.snake_part_list) <= 1):
        return distances
    while x >= snake.x_bounds[0]:
        x -= PLAYER_SPEED
        if any(part.body.colliderect(pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)) for part in snake.snake_part_list[1:]):
            #distances.append(abs(snake.head.x - x))
            distances[0] = abs(snake.head.x - x)
            break
    while x <= snake.x_bounds[1]:
        x += PLAYER_SPEED
        if any(part.body.colliderect(pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)) for part in snake.snake_part_list[1:]):
            #distances.append(abs(snake.head.x - x))
            distances[1] = abs(snake.head.x - x)
            break
    while y >= snake.y_bounds[0]:
        y -= PLAYER_SPEED
        if any(part.body.colliderect(pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)) for part in snake.snake_part_list[1:]):
            #distances.append(abs(snake.head.y - y))
            distances[2] = abs(snake.head.y - y)
            break
    while y <= snake.y_bounds[1]:
        y += PLAYER_SPEED
        if any(part.body.colliderect(pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)) for part in snake.snake_part_list[1:]):
            #distances.append(abs(snake.head.y - y))
            distances[3] = abs(snake.head.y - y)
            break
    return distances
    """

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()
gen = 0

#when we add a snake to the left of the body and it is close to the edge, i think the snake is breaking.

def evaluate(genomes, config):
    global gen
    gen += 1
    nets = []
    snakes = []
    ge = []
    running = True
    stat_font = pygame.font.SysFont("comicsans", 50)
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome,config)
        nets.append(net)
        snakes.append(Snake(screen))
        ge.append(genome)

    for snake in snakes:
        if(snake.current_position != STARTING_POS):
            running = False
            pygame.quit()
            break
#TODO: ONLY GIVE FITNESS FOR REDUCING DISTANCE TO THE COIN, NOT MOVING

    while running and len(snakes) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                break
        #placeholder for the list that will hold all the snakes 
        #fill screen with a color
        screen.fill("black")

        #If a coin is not currently spawned for a snake, then spawn the coin
        for snake in snakes:
            #fitness for being alive longer
            ge[snakes.index(snake)].fitness += 0.1
            snake.spawn_coin()
            snake.draw_coin(screen)
            #Checks to see if each snakes individual coin has been collected
            if(snake.head.colliderect(snake.coin)):
                snake.spawned = False
                snake.add_snake_part()
                ge[snakes.index(snake)].fitness += 20
                snake.start_time = pygame.time.get_ticks()
                snake.prev_moves.clear()
                snake.end_time = 0
                snake.best_distance = 9999


            #If snake is moving closer to the coin then we want to increase its fitness

        for x,snake in enumerate(snakes):
            
            #add current direction plus snake length for now, might add if left/right/up/down is blocked
            x_inputs,y_inputs = calc_inputs(snake)
            x_inputs,y_inputs = calc_input_distances(x_inputs,y_inputs,snake)
            boundary_inputs = calc_bound_distances(snake)
            #distance of snake head to nearest snake part in left, right, down, and up direction
            distances = calc_distance_to_nearest_part(snake) 
            obstacles = check_if_obstacles(snake)           

            inputs = x_inputs + y_inputs + boundary_inputs + distances + obstacles
            inputs.append(len(snake.snake_part_list))
            inputs.append(snake.current_direction[0])
            inputs.append(snake.current_direction[1])
            
            #inputs.append(len(snake.snake_part_list))
            #inputs.append([snake.current_direction[0], snake.current_direction[1]])
            #.append([snake.current_direction[0],snake.current_direction[1]])

            output = nets[snakes.index(snake)].activate(inputs)

            maximum = max(output)
            if maximum == output[0]:
                snake.move_left()
                new_dist = snake.calc_distance()
                snake.previous_distance = snake.current_distance
                snake.current_distance = new_dist
                if snake.current_distance < snake.best_distance:
                    ge[snakes.index(snake)].fitness += 0.2
                    snake.best_distance = snake.current_distance
            elif maximum == output[1]:
                snake.move_right()
                new_dist = snake.calc_distance()
                snake.previous_distance = snake.current_distance
                snake.current_distance = new_dist
                if snake.current_distance < snake.best_distance:
                    ge[snakes.index(snake)].fitness += 0.2
                    snake.best_distance = snake.current_distance
            elif maximum == output[2]:
                snake.move_up()
                new_dist = snake.calc_distance()
                snake.previous_distance = snake.current_distance
                snake.current_distance = new_dist
                if snake.current_distance < snake.best_distance:
                    ge[snakes.index(snake)].fitness += 0.2
                    snake.best_distance = snake.current_distance
            elif maximum == output[3]:
                snake.move_down()
                new_dist = snake.calc_distance()
                snake.previous_distance = snake.current_distance
                snake.current_distance = new_dist
                if snake.current_distance < snake.best_distance:
                    ge[snakes.index(snake)].fitness += 0.2
                    snake.best_distance = snake.current_distance
        # This will manage the movement and drawing of each snake in the list
        for snake in snakes:
            if snake.check_for_collision():
                ge[snakes.index(snake)].fitness -= 10
                nets.pop(snakes.index(snake))
                ge.pop(snakes.index(snake))
                snakes.pop(snakes.index(snake))
        #This will manage the movement and drawing of each snake in the list
        #for snake in snakes:
            #if snake.check_for_collision():
                #ge[snakes.index(snake)].fitness -= 1
                #nets.pop(snakes.index(snake))
                #ge.pop(snakes.index(snake))
                #snakes.pop(snakes.index(snake))
                
            
        for snake in snakes:
            if check_if_inbounds(snake):
                ge[snakes.index(snake)].fitness -= 10
                nets.pop(snakes.index(snake))
                ge.pop(snakes.index(snake))
                snakes.pop(snakes.index(snake))
                snake.reset_snake()

        for snake in snakes:
            if len(snake.snake_part_list) < 10 and snake.current_position in snake.prev_moves:
                ge[snakes.index(snake)].fitness -= 0.2
            
            if ge[snakes.index(snake)].fitness < -5:
                nets.pop(snakes.index(snake))
                ge.pop(snakes.index(snake))
                snakes.pop(snakes.index(snake))
                snake.reset_snake()

            #Need to change this function when AI is implemented
            snake.draw_snake(screen)
            score_label = stat_font.render("Gen: " + str(gen-1),1,(255,255,255))
            screen.blit(score_label, (10, 50))



        #show display to the screen
        pygame.display.flip()
        #We are running every second 60 frames
        #pygame.time.Clock().tick(400)
    for snake in snakes:
        snake.reset_snake()

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)
    
    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    winner = pop.run(evaluate, 10000)
    best_network = neat.nn.FeedForwardNetwork.create(winner, config)
    
    with open('best_snake.txt', 'w') as file:
        file.write(str(best_network))
    print("\nBest snake: \n{!s}".format(winner))    
    


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,'config_feedforward.txt')
    run(config_path)