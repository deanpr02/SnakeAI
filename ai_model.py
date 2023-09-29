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
        self.current_distance = -1
        self.previous_distance = 9999
        self.best_distance = 9999
        self.start_time = pygame.time.get_ticks()
        self.end_time = 0
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
            return True
        return False
    
    def reset_snake(self):
        self.snake_part_list.clear()
        self.head.update(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        self.current_position = (0,0)

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
    if(snake.head.right == RIGHT_BOUNDARY):
        #snake.head.update(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        #snake.reset_snake()
        return True
    if(snake.head.top == TOP_BOUNDARY):
        #snake.head.update(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        #snake.reset_snake()
        return True
    if(snake.head.left == LEFT_BOUNDARY):
        #snake.head.update(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        #snake.reset_snake()
        return True
    if(snake.head.bottom == BOTTOM_BOUNDARY):
        #snake.head.update(STARTING_POS[0],STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        #snake.reset_snake()
        return True
    snake.current_position = (snake.head.x,snake.head.y)
    return False

def calc_time(snakes):
    for snake in snakes:
        time_without_coin = pygame.time.get_ticks() - snake.start_time
        snake.end_time = time_without_coin

        




pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()
gen = 0


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
            snake.spawn_coin()
            snake.draw_coin(screen)
            #Checks to see if each snakes individual coin has been collected
            if(snake.head.colliderect(snake.coin)):
                snake.spawned = False
                snake.add_snake_part()
                ge[snakes.index(snake)].fitness += 10
                snake.start_time = pygame.time.get_ticks()
                snake.end_time = 0

            #If snake is moving closer to the coin then we want to increase its fitness

        for x,snake in enumerate(snakes):

            distance = snake.calc_distance()
            output = nets[snakes.index(snake)].activate((snake.current_position[0],snake.current_position[1],distance))

            maximum = max(output[3],max(output[2],max(output[1],output[2])))
            if maximum == output[0]:
                snake.move_left()
                new_dist = snake.calc_distance()
                snake.previous_distance = snake.current_distance
                snake.current_distance = new_dist
                if snake.current_distance < snake.best_distance:
                    ge[snakes.index(snake)].fitness += 0.1
                    snake.best_distance = snake.current_distance
            elif maximum == output[1]:
                snake.move_right()
                new_dist = snake.calc_distance()
                snake.previous_distance = snake.current_distance
                snake.current_distance = new_dist
                if snake.current_distance < snake.best_distance:
                    ge[snakes.index(snake)].fitness += 0.1
                    snake.best_distance = snake.current_distance
            elif maximum == output[2]:
                snake.move_up()
                new_dist = snake.calc_distance()
                snake.previous_distance = snake.current_distance
                snake.current_distance = new_dist
                if snake.current_distance < snake.best_distance:
                    ge[snakes.index(snake)].fitness += 0.1
                    snake.best_distance = snake.current_distance
            elif maximum == output[3]:
                snake.move_down()
                new_dist = snake.calc_distance()
                snake.previous_distance = snake.current_distance
                snake.current_distance = new_dist
                if snake.current_distance < snake.best_distance:
                    ge[snakes.index(snake)].fitness += 0.1
                    snake.best_distance = snake.current_distance

        #This will manage the movement and drawing of each snake in the list
        for snake in snakes:
            if snake.check_for_collision():
                ge[snakes.index(snake)].fitness -= 1
                nets.pop(snakes.index(snake))
                ge.pop(snakes.index(snake))
                snakes.pop(snakes.index(snake))
                
            
        for snake in snakes:
            if check_if_inbounds(snake):
                ge[snakes.index(snake)].fitness -= 1
                nets.pop(snakes.index(snake))
                ge.pop(snakes.index(snake))
                snakes.pop(snakes.index(snake))

        for snake in snakes:
            if (snake.end_time/1000) > 2:
                ge[snakes.index(snake)].fitness -= 1
                nets.pop(snakes.index(snake))
                ge.pop(snakes.index(snake))
                snakes.pop(snakes.index(snake))

            #Need to change this function when AI is implemented
            snake.draw_snake(screen)
            calc_time(snakes)
            score_label = stat_font.render("Gen: " + str(gen-1),1,(255,255,255))
            screen.blit(score_label, (10, 50))



        #show display to the screen
        pygame.display.flip()
        #We are running every second 60 frames
        #pygame.time.Clock().tick(60)

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)
    
    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    winner = pop.run(evaluate, 50)

    print("\nBest snake: \n{!s}".format(winner))

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,'config_feedforward.txt')
    run(config_path)

