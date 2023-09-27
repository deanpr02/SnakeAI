import pygame
import random
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720
RIGHT_BOUNDARY = 720
LEFT_BOUNDARY = 0
TOP_BOUNDARY = 0
BOTTOM_BOUNDARY = 720
PLAYER_WIDTH = 16
PLAYER_HEIGHT = 16


#TODO:
#This will need to have some changes to accomodate neural network
#1. Need to add for loops so we can loop over multiple snakes
#2. GIVE SOME FITNESS FOR BEING CLOSE TO THE COINS AND GIVE FITNESS FOR COLLECTING COINS; LOSE FITNESS FOR RUNNING INTO OWN SNAKE OR RUNNING INTO BOUNDARY
#3. NEED FOUR OUTPUTS WHICH WILL REPRESENT LEFT,RIGHT,UP,DOWN DEPENDING ON WHAT OUTPUT VALUE IS GREATEST WILL BE THE VALUE THAT CHANGES
#wE WILL NEED TO PASS THE DISTANCE FROM THE COIN SO THE NETWORK KNOWS WHERE TO GO.
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
    def __init__(self):
        self.len_of_snake = 1
        self.current_position = (0,0)
        self.current_direction = (0,0)
        self.hit_box = pygame.Rect(0,0,2,2)
        #We will want this because it will allow us to add a snake part to the end of the snake
        #Each snake part will could have its own direction so we will have an attribute in the
        #SnakePart class that will have its current direction, then based on this we can
        #Add a particular snake part in a certain position.
        self.snake_part_list = []

    #This will trigger when we go over a coin
    def add_snake_part(self,snake_rect):
        new_part = pygame.Rect(self.current_position[0],self.current_position[1],PLAYER_WIDTH,PLAYER_WIDTH)
        last_snake_item = pygame.Rect(snake_rect.x,snake_rect.y,PLAYER_WIDTH,PLAYER_WIDTH)
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
        if(last_snake_item_direction == (0,-2)):
            new_part.top = last_snake_item.bottom
            new_part.y += 2
        if(last_snake_item_direction == (0,2)):
            new_part.bottom = last_snake_item.top
            new_part.y -= 2
        if(last_snake_item_direction == (-2,0)):
            new_part.left = last_snake_item.right
            new_part.x += 2
        if(last_snake_item_direction == (2,0)):
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

    def move_snake(self):
        for snake_part in self.snake_part_list:
            snake_part.move_part()

    def draw_snake_parts(self):
        for snake_part in self.snake_part_list:
            outline = pygame.Rect(snake_part.body.x-1,snake_part.body.y-1,PLAYER_WIDTH+2,PLAYER_HEIGHT+2)
            pygame.draw.rect(screen,"white",outline,PLAYER_WIDTH+2)
            pygame.draw.rect(screen,"red",snake_part.body,PLAYER_WIDTH)




#Game-Specific Functions
def manage_player_movement(player, head, outline):
    if player.current_direction == dir_dict["UP"]:
        head.move_ip(0,-2)
    if player.current_direction == dir_dict["DOWN"]:
        head.move_ip(0,2)
    if player.current_direction == dir_dict["LEFT"]:
        head.move_ip(-2,0)
    if player.current_direction == dir_dict["RIGHT"]:
        head.move_ip(2,0)
    outline.update(head.x-1,head.y-1,PLAYER_WIDTH+2,PLAYER_HEIGHT+2)
    player.hit_box.update(head.x+(PLAYER_WIDTH/2-1),head.y+(PLAYER_HEIGHT/2-1),2,2)

#After the occurence of a "game-over" event, this function will reset the game aka reset the snake length and position of the head to the middle of the screen.
def reset_game(player):
    player.current_direction = (0,0)
    player.snake_part_list = []


#Check to see if a player has touched the side of the screen
def check_if_inbounds(snake_head, player):
    if(snake_head.right == RIGHT_BOUNDARY):
        snake_head.update(starting_pos.x,starting_pos.y,PLAYER_WIDTH,PLAYER_HEIGHT)
        reset_game(player)
        return
    if(snake_head.top == TOP_BOUNDARY):
        snake_head.update(starting_pos.x,starting_pos.y,PLAYER_WIDTH,PLAYER_HEIGHT)
        reset_game(player)
        return
    if(snake_head.left == LEFT_BOUNDARY):
        snake_head.update(starting_pos.x,starting_pos.y,PLAYER_WIDTH,PLAYER_HEIGHT)
        reset_game(player)
        return
    if(snake_head.bottom == BOTTOM_BOUNDARY):
        snake_head.update(starting_pos.x,starting_pos.y,PLAYER_WIDTH,PLAYER_HEIGHT)
        reset_game(player)
        return
    player.current_position = (snake_head.x,snake_head.y)

def check_for_collision(snake_head,player):
    snake_part_rects = [rect.body for rect in player.snake_part_list]
    if(player.hit_box.collideobjects(snake_part_rects)):
        snake_head.update(starting_pos.x,starting_pos.y,PLAYER_WIDTH,PLAYER_HEIGHT)
        reset_game(player)

def get_directions(player):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player.current_direction = dir_dict["UP"]
        player.queue_directions(dir_dict["UP"])
    elif keys[pygame.K_s]:
        player.current_direction = dir_dict["DOWN"]
        player.queue_directions(dir_dict["DOWN"])
    elif keys[pygame.K_a]:
        player.current_direction = dir_dict["LEFT"]
        player.queue_directions(dir_dict["LEFT"])
    elif keys[pygame.K_d]:
        player.current_direction = dir_dict["RIGHT"]
        player.queue_directions(dir_dict["RIGHT"])


pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
clock = pygame.time.Clock()
my_font = pygame.font.SysFont('Comic Sans MS',20)
starting_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

running = True
movement_dir = ""
collected = False
dir_dict = {"LEFT": (-2,0),"RIGHT":(2,0),"UP":(0,-2),"DOWN":(0,2)}

#This is the class that references the entire Snake class which will be composed
#of a bunch of snake parts
player = Snake()
#This represents the head of the snake which will be responding to player input controls
snake_head = pygame.Rect(starting_pos.x,starting_pos.y,PLAYER_WIDTH,PLAYER_HEIGHT)
#Represents the item which will grow the snake
item_to_collect = pygame.Rect(starting_pos.x, starting_pos.y,PLAYER_WIDTH,PLAYER_HEIGHT)
#Outline around snake_head to make it more defined looking
outline = pygame.Rect(starting_pos.x-2,starting_pos.y-2,PLAYER_WIDTH+2,PLAYER_HEIGHT+2)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    #fill screen with a color
    screen.fill("black")
    text_surface = my_font.render(f"Score: {len(player.snake_part_list)}",False,"white")
    screen.blit(text_surface,(0,0))

    #Randomize location for the collectable item
    if(not collected):
        item_to_collect.update(random.random()*(SCREEN_WIDTH-20),random.random()*(SCREEN_HEIGHT-20),PLAYER_WIDTH,PLAYER_HEIGHT)
        collected = True

    #Checks to see if a item has been collected; if it has then add a snake and allow for a new item to be spawned in
    if(snake_head.colliderect(item_to_collect)):
        collected = False
        player.add_snake_part(snake_head)

    #DRAW RECTS

    #Have a method for drawing the snake
    pygame.draw.rect(screen,"yellow",item_to_collect,PLAYER_WIDTH)
    pygame.draw.rect(screen,"white",outline,PLAYER_WIDTH+2)
    pygame.draw.rect(screen,"red",snake_head,PLAYER_WIDTH)
         
    #FUNCTION CALLS
    
    #Get the keys pressed so we can queue the direction of the snake head
    get_directions(player)

    #This creates constant movement in a direction once a WASD key has been pushed; direction
    # will not change until a different WASD key has been pushed. 
    manage_player_movement(player, snake_head, outline)

    #This will move every snake part on the snake
    player.move_snake()

    #This draws all parts of the snake
    player.draw_snake_parts()

    #Checks to see if the player hits the boundary
    check_if_inbounds(snake_head,player)

    #Checks to see if the player hits a part of the snake
    check_for_collision(snake_head,player)

    #show display to the screen
    pygame.display.flip()
    dt = clock.tick(60) / 1000


pygame.quit()
