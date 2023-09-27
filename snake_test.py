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

    #Randomize location for the collectable item
    if(not collected):
        item_to_collect.update(random.random()*(SCREEN_WIDTH-20),random.random()*(SCREEN_HEIGHT-20),PLAYER_WIDTH,PLAYER_HEIGHT)
        collected = True

    #Checks to see if a item has been collected; if it has then add a snake and allow for a new item to be spawned in
    if(snake.head.colliderect(item_to_collect)):
        collected = False
        snake.add_snake_part()

    #DRAW RECTS

    #Have a method for drawing the snake
    pygame.draw.rect(screen,"yellow",item_to_collect,PLAYER_WIDTH)
         
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


