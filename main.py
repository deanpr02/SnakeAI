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


"""
Move the player in a direction corresponding to WASD keys

Args:
    player -> Snake object
    head -> pygame.Rect
    outline -> pygame.Rect
"""
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

"""
After the occurence of a "game-over" event, this function will reset the game aka reset the snake length and position of the head to the middle of the screen.

Args:
    player -> Snake object
"""
def reset_game(player):
    player.current_direction = (0,0)
    player.snake_part_list = []

"""
Check to see if a player has touched the side of the screen

Args:
    player -> Snake object

Return:
    True if no out of bounds, False if out of bounds -> boolean
"""
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

"""
Checks to see if the snake head has connected with any of the snake body

Args:
    player -> Snake object

Return:
    True if there is no collision False if there is a collision -> boolean
"""
def check_for_collision(player):
    snake_part_rects = [rect.body for rect in player.snake_part_list]
    if(player.hit_box.collideobjects(snake_part_rects)):
        player.head.update(ske.STARTING_POS[0],ske.STARTING_POS[1],PLAYER_WIDTH,PLAYER_HEIGHT)
        reset_game(player)
        return False
    return True

"""
Queue the directions the head moves so the snake parts can have a record of what moves they need to make
when they are created

Args:
    player -> Snake object
"""
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

#TODO: Finish this function
"""
If no snake has been trained, run the NEAT algorithm to train one
"""
def train_snake():
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,'config_feedforward.txt')
    run(config_path)


"""
Depending on output from the neural network, choose the move which the network deems maximum gain

Args:
    output -> list of outputs from network
    player -> Snake object
"""
def select_move(output,player):
    #output is in the format of [LEFT,RIGHT,UP,DOWN]
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

"""
Gathers inputs and passes it to the neural network to retrieve outputs to determine next move for snake

Args:
    player -> Snake object
    net -> NEAT Feed Forward network

Return:
    list of outputs for each potential directional move -> list
"""
def get_net_inputs(player,net):
    #add current direction plus snake length for now, might add if left/right/up/down is blocked
    x_inputs,y_inputs = player.calc_inputs()
    x_inputs,y_inputs = player.calc_input_distances(x_inputs,y_inputs)
    boundary_inputs = player.calc_bound_distances()
    #distance of snake head to nearest snake part in left, right, down, and up direction
    obstacles = player.check_if_obstacles()          
    inputs = x_inputs + y_inputs + boundary_inputs + obstacles

    inputs.append(player.current_direction[0])
    inputs.append(player.current_direction[1])

    output = net.activate(inputs)

    return output

"""
Checks to see if a coin has been collected, if there has then spawn a new one

Args:
    player -> Snake object
"""
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

"""
Development function which has lines on the snake in all four directions which disappear opposite of which
direction the snake is moving

Args:
    player -> Snake object
"""
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

#def check_if_coin_collected(snake):
#    #fruit_gain = 3 * len(snake.snake_part_list)
#    snake.spawn_coin()
#    snake.draw_coin(screen)
#    #Checks to see if each snakes individual coin has been collected
#    if(snake.head.colliderect(snake.coin)):
#        snake.spawned = False
#        snake.add_snake_part()
#        snake.start_time = pygame.time.get_ticks()
#        snake.prev_moves.clear()
#        snake.end_time = 0
#        snake.best_distance = 9999
#        snake.timer = 0
#        snake.timer_started = False

"""
Trains a snake using NEAT algorithm if one is not saved, otherwise run the game using the net
"""
def run_ai_snake():
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()
    my_font = pygame.font.SysFont('Comic Sans MS',20)

    running = True

    if os.path.isfile('best_snake.pkl'):
        with open('best_snake.pkl', 'rb') as f:
            net = pickle.load(f)
        print("Loaded best snake")
    else:
        train_snake()
        with open('best_snake.pkl', 'rb') as f:
            net = pickle.load(f)
    
    player = ske.Snake(screen)
    #starting_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    #item_to_collect = pygame.Rect(starting_pos.x, starting_pos.y,PLAYER_WIDTH,PLAYER_HEIGHT)
    #outline = pygame.Rect(starting_pos.x-2,starting_pos.y-2,PLAYER_WIDTH+2,PLAYER_HEIGHT+2)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        #fill screen with a color
        screen.fill("black")
        text_surface = my_font.render(f"Score: {len(player.snake_part_list)}",False,"white")
        screen.blit(text_surface,(0,0))

        check_if_coin_collected(player)
        output = get_net_inputs(player,net)

        select_move(output,player)

        #This draws all parts of the snake
        player.draw_snake(screen)

        #Check for losing conditions
        check_if_inbounds(player)
        check_for_collision(player)

        #show display to the screen
        pygame.display.flip()
        dt = clock.tick(60) / 1000

"""
Runs a user-controlled game of snake
"""
def run_snake():
    pygame.display.set_caption("AI Snake Game")
    clock = pygame.time.Clock()
    my_font = pygame.font.SysFont('Comic Sans MS',20)

    running = True
    collected = False

    player = ske.Snake(screen)
    starting_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    
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
        if(player.head.colliderect(item_to_collect)):
            collected = False
            player.add_snake_part()

        #-----DRAW RECTS-----

        #Have a method for drawing the snake
        pygame.draw.rect(screen,"yellow",item_to_collect,PLAYER_WIDTH)
        pygame.draw.rect(screen,"white",outline,PLAYER_WIDTH+2)
        pygame.draw.rect(screen,"red",player.head,PLAYER_WIDTH)

        #-----FUNCTION CALLS-----

        #Movement processing for snake head/body
        get_directions(player) 
        manage_player_movement(player,player.head,outline)
        player.move_snake_parts()
        player.draw_snake(screen)

        #Checks for losing conditions in the game
        check_if_inbounds(player)
        check_for_collision(player)

        #show display to the screen
        pygame.display.flip()
        dt = clock.tick(60) / 1000

"""
Generates the main menu and allows selection for either a user game or AI training

Return:
    Game selection -> int
"""
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

"""
Entry point for program
"""
def main():
    game_selection = run_main_menu()

    if game_selection == USER:
        run_snake()
    elif game_selection == AI:
        run_ai_snake()
    
    pygame.quit()


if __name__ == "__main__":
    main()