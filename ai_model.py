import pygame
import neat
import os
import math
import time
import pickle
import snake as ske
pygame.font.init()
pygame.init()

#Globals
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720
PLAYER_WIDTH = 16
PLAYER_HEIGHT = 16
SWITCH_GENERATION = 200
PLAYER_SPEED = 2
DIR_DICT = {"LEFT": (-PLAYER_SPEED,0),"RIGHT":(PLAYER_SPEED,0),"UP":(0,-PLAYER_SPEED),"DOWN":(0,PLAYER_SPEED)}
stat_font = pygame.font.SysFont("comicsans", 50)
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Training Snake")
clock = pygame.time.Clock()
total_elapsed_time = 0
gen = 0
collision_cost = 20
fruit_gain = 50
time_alive_gain = 0.0
minimize_distance_gain = 0.0


#Training-Specific Functions
def update_screen(snakes,screen):
    for snake in snakes:
        snake.draw_snake(screen)
        score_label = stat_font.render("Gen: " + str(gen-1),1,(255,255,255))
        screen.blit(score_label, (10, 50))

def check_if_coin_collected(snake,index,ge):
    #fruit_gain = 3 * len(snake.snake_part_list)
    ge[index].fitness += time_alive_gain
    snake.spawn_coin()
    snake.draw_coin(screen)
    #Checks to see if each snakes individual coin has been collected
    if(snake.head.colliderect(snake.coin)):
        snake.spawned = False
        snake.add_snake_part()
        ge[index].fitness += fruit_gain
        snake.start_time = pygame.time.get_ticks()
        snake.prev_moves.clear()
        snake.end_time = 0
        snake.best_distance = 9999
        snake.timer = 0
        snake.timer_started = False
        #snake.time_last_collected = pygame.time.get_ticks()

def if_dead(snake,dir):
    snake_temp = pygame.Rect(0,0,2,2)
    new_x = snake.head.x + DIR_DICT[dir][0]
    new_y = snake.head.y + DIR_DICT[dir][1]
    snake_temp.update(new_x+(PLAYER_WIDTH/2-1),new_y+(PLAYER_HEIGHT/2-1),2,2)
    snake_part_rects = [rect.body for rect in snake.snake_part_list]
    if(snake_temp.collideobjects(snake_part_rects)):
            return True
    return False

#-6
def initialize_phase1_net_inputs(snake,index,nets):
    #add current direction plus snake length for now, might add if left/right/up/down is blocked
    x_inputs,y_inputs = snake.calc_inputs()
    x_inputs,y_inputs = snake.calc_input_distances(x_inputs,y_inputs)
    boundary_inputs = snake.calc_bound_distances()
    #distance of snake head to nearest snake part in left, right, down, and up direction
    #distances = snake.calc_distance_to_nearest_part() 
    obstacles = snake.check_if_obstacles()          
    inputs = x_inputs + y_inputs + boundary_inputs + obstacles
    #inputs.append(len(snake.snake_part_list))
    inputs.append(snake.current_direction[0])
    inputs.append(snake.current_direction[1])

    output = nets[index].activate(inputs)

    return output

#-5
def initialize_phase2_net_inputs(snake,index,nets):
    #add current direction plus snake length for now, might add if left/right/up/down is blocked
    x_inputs,y_inputs = snake.calc_inputs()
    x_inputs,y_inputs = snake.calc_input_distances(x_inputs,y_inputs)
    boundary_inputs = snake.calc_bound_distances()
    #distance of snake head to nearest snake part in left, right, down, and up direction
    distances = snake.calc_distance_to_nearest_part() 
    obstacles = snake.check_if_obstacles()          
    inputs = x_inputs + y_inputs + boundary_inputs + distances + obstacles
    inputs.append(len(snake.snake_part_list))
    inputs.append(snake.current_direction[0])
    inputs.append(snake.current_direction[1])

    output = nets[index].activate(inputs)

    return output

def predict_move(snake,output,index,ge):
    maximum = max(output)
    if maximum == output[0]:
        snake.move_left()
        new_dist = snake.calc_distance()
        snake.previous_distance = snake.current_distance
        snake.current_distance = new_dist
        if snake.current_distance < snake.best_distance:
            ge[index].fitness += minimize_distance_gain
            snake.best_distance = snake.current_distance
    elif maximum == output[1]:
        snake.move_right()
        new_dist = snake.calc_distance()
        snake.previous_distance = snake.current_distance
        snake.current_distance = new_dist
        if snake.current_distance < snake.best_distance:
            ge[index].fitness += minimize_distance_gain
            snake.best_distance = snake.current_distance
    elif maximum == output[2]:
        snake.move_up()
        new_dist = snake.calc_distance()
        snake.previous_distance = snake.current_distance
        snake.current_distance = new_dist
        if snake.current_distance < snake.best_distance:
            ge[index].fitness += minimize_distance_gain
            snake.best_distance = snake.current_distance
    elif maximum == output[3]:
        snake.move_down()
        new_dist = snake.calc_distance()
        snake.previous_distance = snake.current_distance
        snake.current_distance = new_dist
        if snake.current_distance < snake.best_distance:
            ge[index].fitness += minimize_distance_gain
            snake.best_distance = snake.current_distance

def predict_move2(snake,output,index,ge):
    directions = {0:"LEFT",1:"RIGHT",2:"UP",3:"DOWN"}
    while True:
        maximum_index = output.index(max(output))
        if if_dead(snake,directions[maximum_index]):
            output[maximum_index] = -float('inf')
            continue
        maximum = output[maximum_index]
        break
    if maximum == output[0]:
        snake.move_left()
        new_dist = snake.calc_distance()
        snake.previous_distance = snake.current_distance
        snake.current_distance = new_dist
        if snake.current_distance < snake.best_distance:
            ge[index].fitness += minimize_distance_gain
            snake.best_distance = snake.current_distance
    elif maximum == output[1]:
        snake.move_right()
        new_dist = snake.calc_distance()
        snake.previous_distance = snake.current_distance
        snake.current_distance = new_dist
        if snake.current_distance < snake.best_distance:
            ge[index].fitness += minimize_distance_gain
            snake.best_distance = snake.current_distance
    elif maximum == output[2]:
        snake.move_up()
        new_dist = snake.calc_distance()
        snake.previous_distance = snake.current_distance
        snake.current_distance = new_dist
        if snake.current_distance < snake.best_distance:
            ge[index].fitness += minimize_distance_gain
            snake.best_distance = snake.current_distance
    elif maximum == output[3]:
        snake.move_down()
        new_dist = snake.calc_distance()
        snake.previous_distance = snake.current_distance
        snake.current_distance = new_dist
        if snake.current_distance < snake.best_distance:
            ge[index].fitness += minimize_distance_gain
            snake.best_distance = snake.current_distance
            
def is_snake_collision(snakes,snake,index,ge,nets):
    if snake.check_for_collision():
        ge[index].fitness -= collision_cost
        nets.pop(index)
        ge.pop(index)
        snakes.pop(snakes.index(snake))

def is_snake_inbounds(snakes,snake,index,ge,nets):
    if snake.check_if_inbounds():
        ge[index].fitness -= collision_cost
        nets.pop(index)
        ge.pop(index)
        snakes.pop(index)
        snake.reset_snake()

def purge_stagnation(snakes,snake,index,ge,nets):
    if len(snake.snake_part_list) < 10 and snake.current_position in snake.prev_moves:
        ge[index].fitness -= 0.2
            
    if ge[index].fitness < -5:
        nets.pop(index)
        ge.pop(index)
        snakes.pop(index)
        snake.reset_snake()
        return
    """
    snake.timer = (pygame.time.get_ticks() - snake.time_last_collected) // 1000
    if(snake.timer == 5):
        ge[index].fitness -= 100
        nets.pop(index)
        ge.pop(index)
        snakes.pop(index)
        """

def calc_time(snake,index,ge):
    if not snake.timer_started:
        snake.start_time = time.time()
        snake.timer_started = True
    end_time = time.time()
    snake.timer = (end_time - snake.start_time)
    if(snake.timer >= 7):
        ge[index].fitness -= 1000
    

def calc_distance(obj1, obj2):
    x_dist = obj2[0] - obj1[0]
    x_dist = x_dist ** 2
    y_dist = obj2[1] - obj1[1]
    y_dist = y_dist ** 2
    dist = math.sqrt(x_dist,y_dist)
    return dist

def eval_movement(genomes,config):
    global gen,collision_cost,fruit_gain,time_alive_gain,minimize_distance_gain
    gen += 1
    nets = []
    snakes = []
    ge = []
    running = True
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome,config)
        nets.append(net)
        snakes.append(ske.Snake(screen))
        ge.append(genome)

    while running and len(snakes) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                break
        #fill screen with a color
        screen.fill("black")
        for x,snake in enumerate(snakes):
            calc_time(snake,snakes.index(snake),ge)
            check_if_coin_collected(snake,snakes.index(snake),ge)
            output = initialize_phase1_net_inputs(snake,snakes.index(snake),nets)
            predict_move(snake,output,snakes.index(snake),ge)
            if snake not in snakes:
                continue    
            is_snake_collision(snakes,snake,x,ge,nets)
            if snake not in snakes:
                continue
            is_snake_inbounds(snakes,snake,x,ge,nets)
            if snake not in snakes:
                continue
            purge_stagnation(snakes,snake,x,ge,nets)

        update_screen(snakes,screen)

        #show display to the screen
        pygame.display.flip()

        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
            for snake in snakes:
                snake.start_time = time.time()
            pygame.time.Clock().tick(60)
            
        #We are running every second 60 frames
        #pygame.time.Clock().tick(400)
    for snake in snakes:
        snake.reset_snake()

def eval_avoidance(genomes,config):
    global gen,collision_cost,fruit_gain,time_alive_gain,minimize_distance_gain
    gen += 1
    collision_cost = 50
    fruit_gain = 20
    time_alive_gain = 0.1
    nets = []
    snakes = []
    ge = []
    running = True
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome,config)
        nets.append(net)
        snakes.append(ske.Snake(screen))
        ge.append(genome)

    while running and len(snakes) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                break
        #fill screen with a color
        screen.fill("black")
        for x,snake in enumerate(snakes):
            calc_time(snake,snakes.index(snake),ge)
            check_if_coin_collected(snake,snakes.index(snake),ge)
            output = initialize_phase2_net_inputs(snake,snakes.index(snake),nets)
            predict_move(snake,output,snakes.index(snake),ge)
            if snake not in snakes:
                continue    
            is_snake_collision(snakes,snake,x,ge,nets)
            if snake not in snakes:
                continue
            is_snake_inbounds(snakes,snake,x,ge,nets)
            if snake not in snakes:
                continue
            purge_stagnation(snakes,snake,x,ge,nets)

        update_screen(snakes,screen)

        #show display to the screen
        pygame.display.flip()

        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
            for snake in snakes:
                snake.start_time = time.time()
            pygame.time.Clock().tick(60)
            
        #We are running every second 60 frames
        #pygame.time.Clock().tick(400)
    for snake in snakes:
        snake.reset_snake()

def run(config_file):
    #config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)
    
    #pop = neat.Population(config)
    #pop.add_reporter(neat.StdOutReporter(True))
    #stats = neat.StatisticsReporter()
    #pop.add_reporter(stats)

    
    #training of the snake for movement
    #winner = pop.run(eval_movement, 400)
    #phase1_best_network = neat.nn.FeedForwardNetwork.create(winner, config)
    #saving the snake for use in the next training phase
    #with open('phase_1_snake.pkl', 'wb') as file:
        #pickle.dump((pop.population,pop.species),file)
    
    #print("\nBest snake from Phase 1: \n{!s}".format(winner))

    with open('phase_1_snake.pkl','rb') as file:
        best_genomes,species = pickle.load(file)
        generations = 0



    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,'config_p2_feedforward.txt')
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation,config_path)
    
    pop = neat.Population(config,initial_state=(best_genomes,species,generations))
    #config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    
    #pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    winner = pop.run(eval_avoidance,1500)
    phase2_best_network = neat.nn.FeedForwardNetwork.create(winner,config)
    with open('phase_2_snake.pkl','wb') as file:
        pickle.dump(phase2_best_network,file)
    
    print("\nBest snake from Phase 2: \n{!s}".format(winner))
    


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,'config_p1_feedforward.txt')
    run(config_path)


#for round 1 we have the distances to the coins, round 2 we have distances to the body