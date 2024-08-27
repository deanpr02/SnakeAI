import pygame
import random
import os
from ai_model import run
import snake as ske
import pickle
from globals import screen
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720
RIGHT_BOUNDARY = 720
LEFT_BOUNDARY = 0
TOP_BOUNDARY = 0
BOTTOM_BOUNDARY = 720
PLAYER_WIDTH = 16
PLAYER_HEIGHT = 16
USER = 0
AI = 1


#Game-Specific Functions
def manage_player_movement(player, head, outline):
    if player.current_direction == ske.DIR_DICT["UP"]:
        head.move_ip(0,-2)
    if player.current_direction == ske.DIR_DICT["DOWN"]:
        head.move_ip(0,2)
    if player.current_direction == ske.DIR_DICT["LEFT"]:
        head.move_ip(-2,0)
    if player.current_direction == ske.DIR_DICT["RIGHT"]:
        head.move_ip(2,0)
    outline.update(head.x-1,head.y-1,PLAYER_WIDTH+2,PLAYER_HEIGHT+2)
    player.hit_box.update(head.x+(PLAYER_WIDTH/2-1),head.y+(PLAYER_HEIGHT/2-1),2,2)

#After the occurence of a "game-over" event, this function will reset the game aka reset the snake length and position of the head to the middle of the screen.
def reset_game(player):
    player.current_direction = (0,0)
    player.snake_part_list = []

"""
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
"""

#Check to see if a player has touched the side of the screen
def check_if_inbounds(player):
    if(player.head.right == RIGHT_BOUNDARY):
        player.head.update(ske.STARTING_POS[0],ske.STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        reset_game(player)
        return False
    if(player.head.top == TOP_BOUNDARY):
        player.head.update(ske.STARTING_POS[0],ske.STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        reset_game(player)
        return False
    if(player.head.left == LEFT_BOUNDARY):
        player.head.update(ske.STARTING_POS[0],ske.STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        reset_game(player)
        return False
    if(player.head.bottom == BOTTOM_BOUNDARY):
        player.head.update(ske.STARTING_POS[0],ske.STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        reset_game(player)
        return False
    player.current_position = (player.head.x,player.head.y)
    return True

def check_for_collision(player):
    snake_part_rects = [rect.body for rect in player.snake_part_list]
    if(player.hit_box.collideobjects(snake_part_rects)):
        player.head.update(ske.STARTING_POS[0],ske.STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        reset_game(player)
        return False
    return True


def get_directions(player):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player.current_direction = ske.DIR_DICT["UP"]
        player.queue_directions(ske.DIR_DICT["UP"])
    elif keys[pygame.K_s]:
        player.current_direction = ske.DIR_DICT["DOWN"]
        player.queue_directions(ske.DIR_DICT["DOWN"])
    elif keys[pygame.K_a]:
        player.current_direction = ske.DIR_DICT["LEFT"]
        player.queue_directions(ske.DIR_DICT["LEFT"])
    elif keys[pygame.K_d]:
        player.current_direction = ske.DIR_DICT["RIGHT"]
        player.queue_directions(ske.DIR_DICT["RIGHT"])

def train_snake():
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,'config_feedforward.txt')
    run(config_path)

def select_move(output,player):
    maximum = max(output)
    if maximum == output[0]:
        player.move_left()
        new_dist = player.calc_distance()
        player.previous_distance = player.current_distance
        player.current_distance = new_dist
    elif maximum == output[1]:
        player.move_right()
        new_dist = player.calc_distance()
        player.previous_distance = player.current_distance
        player.current_distance = new_dist
    elif maximum == output[2]:
        player.move_up()
        new_dist = player.calc_distance()
        player.previous_distance = player.current_distance
        player.current_distance = new_dist
    elif maximum == output[3]:
        player.move_down()
        new_dist = player.calc_distance()
        player.previous_distance = player.current_distance
        player.current_distance = new_dist



def get_net_inputs(player,net):
    #add current direction plus snake length for now, might add if left/right/up/down is blocked
    x_inputs,y_inputs = player.calc_inputs()
    x_inputs,y_inputs = player.calc_input_distances(x_inputs,y_inputs)
    boundary_inputs = player.calc_bound_distances()
    #distance of snake head to nearest snake part in left, right, down, and up direction
    #distances = snake.calc_distance_to_nearest_part() 
    obstacles = player.check_if_obstacles()          
    inputs = x_inputs + y_inputs + boundary_inputs + obstacles
    #inputs.append(len(snake.snake_part_list))
    inputs.append(player.current_direction[0])
    inputs.append(player.current_direction[1])

    output = net.activate(inputs)

    return output


def check_if_coin_collected(player):
    player.spawn_coin()
    player.draw_coin(screen)
    #Checks to see if each snakes individual coin has been collected
    if(player.head.colliderect(player.coin)):
        player.spawned = False
        player.add_snake_part()
        player.start_time = pygame.time.get_ticks()
        player.prev_moves.clear()
        player.end_time = 0
        player.best_distance = 9999


def update_dev_lines(player):
    x_pos,y_pos = player.head.x,player.head.y
    obstacles = player.check_if_obstacles()
    #left line
    if obstacles[0] == False:
        pygame.draw.line(screen,"BLACK",(0,y_pos),(x_pos,y_pos))
    else:
        pygame.draw.line(screen,"WHITE",(0,y_pos),(x_pos,y_pos))
    #right line
    if obstacles[1] == False:
        pygame.draw.line(screen,"BLACK",(x_pos+PLAYER_WIDTH,y_pos),(SCREEN_WIDTH,y_pos))
    else:
        pygame.draw.line(screen,"WHITE",(x_pos+PLAYER_WIDTH,y_pos),(SCREEN_WIDTH,y_pos))
        #up
    if obstacles[2] == False:
        pygame.draw.line(screen,"BLACK",(x_pos,0),(x_pos,y_pos))
    else:
        pygame.draw.line(screen,"WHITE",(x_pos,0),(x_pos,y_pos))
        #down
    if obstacles[3] == False:
        pygame.draw.line(screen,"BLACK",(x_pos,y_pos+PLAYER_HEIGHT),(x_pos,SCREEN_HEIGHT))
    else:
        pygame.draw.line(screen,"WHITE",(x_pos,y_pos+PLAYER_HEIGHT),(x_pos,SCREEN_HEIGHT))

def check_if_coin_collected(snake):
    #fruit_gain = 3 * len(snake.snake_part_list)
    snake.spawn_coin()
    snake.draw_coin(screen)
    #Checks to see if each snakes individual coin has been collected
    if(snake.head.colliderect(snake.coin)):
        snake.spawned = False
        snake.add_snake_part()
        snake.start_time = pygame.time.get_ticks()
        snake.prev_moves.clear()
        snake.end_time = 0
        snake.best_distance = 9999
        snake.timer = 0
        snake.timer_started = False


def run_ai_snake():
    #pygame.font.init()
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()
    my_font = pygame.font.SysFont('Comic Sans MS',20)

    running = True
    movement_dir = ""
    collected = False

    if os.path.isfile('phase_1_snake.pkl'):
        with open('phase_1_snake.pkl', 'rb') as f:
            net = pickle.load(f)
        print("Loaded best snake")
    
    player = ske.Snake(screen)
    starting_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    item_to_collect = pygame.Rect(starting_pos.x, starting_pos.y,PLAYER_WIDTH,PLAYER_HEIGHT)
    outline = pygame.Rect(starting_pos.x-2,starting_pos.y-2,PLAYER_WIDTH+2,PLAYER_HEIGHT+2)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        #fill screen with a color
        screen.fill("black")
        text_surface = my_font.render(f"Score: {len(player.snake_part_list)}",False,"white")
        screen.blit(text_surface,(0,0))

        check_if_coin_collected(player)
        #manage_player_movement(player,player.head, outline)
        output = get_net_inputs(player,net)

        select_move(output,player)

        #This draws all parts of the snake
        player.draw_snake(screen)

        #Checks to see if the player hits the boundary
        check_if_inbounds(player)

        #Checks to see if the player hits a part of the snake
        check_for_collision(player)

        #show display to the screen
        pygame.display.flip()
        dt = clock.tick(60) / 1000

def run_snake():
    #pygame.init()
    #pygame.font.init()
    #screen2 = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    pygame.display.set_caption("AI Snake Game")
    clock = pygame.time.Clock()
    my_font = pygame.font.SysFont('Comic Sans MS',20)

    running = True
    movement_dir = ""
    collected = False

    if os.path.isfile('phase_1_snake.pkl'):
        with open('phase_1_snake.pkl', 'rb') as f:
            net = pickle.load(f)
        print("Loaded best snake")

    player = ske.Snake(screen)
    #snake_head = player.head
    starting_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    #This is the class that references the entire Snake class which will be composed
    #of a bunch of snake parts
    #player = ske.Snake(screen)
    #This represents the head of the snake which will be responding to player input controls
    #snake_head = pygame.Rect(starting_pos.x,starting_pos.y,PLAYER_WIDTH,PLAYER_HEIGHT)
    #Represents the item which will grow the snake
    item_to_collect = pygame.Rect(starting_pos.x, starting_pos.y,PLAYER_WIDTH,PLAYER_HEIGHT)
    #Outline around snake_head to make it more defined looking
    outline = pygame.Rect(starting_pos.x-2,starting_pos.y-2,PLAYER_WIDTH+2,PLAYER_HEIGHT+2)

    #snakes = [player]
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
        if(player.head.colliderect(item_to_collect)):
            collected = False
            player.add_snake_part()

        #DRAW RECTS

        #Have a method for drawing the snake
        pygame.draw.rect(screen,"yellow",item_to_collect,PLAYER_WIDTH)
        pygame.draw.rect(screen,"white",outline,PLAYER_WIDTH+2)
        pygame.draw.rect(screen,"red",player.head,PLAYER_WIDTH)

        #FUNCTION CALLS

        #Get the keys pressed so we can queue the direction of the snake head
        get_directions(player)

        #This creates constant movement in a direction once a WASD key has been pushed; direction
        # will not change until a different WASD key has been pushed. 
        manage_player_movement(player,player.head, outline)

        #This will move every snake part on the snake
        player.move_snake_parts()

        #This draws all parts of the snake
        player.draw_snake(screen)

        #update_dev_lines(player)

        #Checks to see if the player hits the boundary
        check_if_inbounds(player)

        #Checks to see if the player hits a part of the snake
        check_for_collision(player)

        #show display to the screen
        pygame.display.flip()
        dt = clock.tick(60) / 1000

def run_main_menu():
    regular_game_rect = pygame.Rect(120,450,150,85)
    ai_game_rect = pygame.Rect(450,450,150,85)
    
    welcome_font = pygame.font.SysFont('Comic Sans MS',50)
    type_font = pygame.font.SysFont('Comic Sans MS',20)

    game_selection = None
    running = True
    while(running):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if regular_game_rect.collidepoint(event.pos):
                    game_selection = USER
                    running = False
                if ai_game_rect.collidepoint(event.pos):
                    game_selection = AI
                    running = False

        pygame.draw.rect(screen,"RED",regular_game_rect,0)
        pygame.draw.rect(screen,"BLUE",ai_game_rect,0)
        welcome_surface = welcome_font.render("Welcome to Snake!",False,"white")
        snake_surface = type_font.render("User Game",False,"white")
        ai_surface = type_font.render("Train a Snake",False,"white")
        
        screen.blit(welcome_surface,(140,0))
        screen.blit(snake_surface,(140,475))
        screen.blit(ai_surface,(460,475))

        pygame.display.flip()

    screen.fill("BLACK")
    return game_selection


def main():
    game_selection = run_main_menu()

    if game_selection == USER:
        run_snake()
    elif game_selection == AI:
        run_ai_snake()
    
    pygame.quit()


if __name__ == "__main__":
    main()