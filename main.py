import pygame
import os
import random
import math
import sys
import neat

pygame.init()

# Global Constants
TELA_ALTURA = 600
TELA_LARGURA = 1100
TELA = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))

CORRENDO = [pygame.image.load(os.path.join("Assets/wesley", "wrun1.png")),
           pygame.image.load(os.path.join("Assets/wesley", "wrun2.png")),
           pygame.image.load(os.path.join("Assets/wesley", "wrun3.png")),
           pygame.image.load(os.path.join("Assets/wesley", "wrun4.png")),
           pygame.image.load(os.path.join("Assets/wesley", "wrun5.png")),
           pygame.image.load(os.path.join("Assets/wesley", "wrun6.png")),
           ]

PULANDO = pygame.image.load(os.path.join("Assets/wesley", "wjump.png"))

CACTUS_PEQUENO = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
CACTUS_GRANDE = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

FONTE = pygame.font.Font('freesansbold.ttf', 20)


class Wesley:
    X_POS = 80
    Y_POS = 310
    JUMP_VEL = 8.5

    def __init__(self, img=CORRENDO[0]):
        self.image = img
        self.wesley_run = True
        self.wesley_jump = False
        self.jump_vel = self.JUMP_VEL
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, img.get_width(), img.get_height())
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.step_index = 0

    def update(self):
        if self.wesley_run:
            self.run()
        if self.wesley_jump:
            self.jump()
        if self.step_index >= 10:
            self.step_index = 0

    def jump(self):
        self.image = PULANDO
        if self.wesley_jump:
            self.rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel <= -self.JUMP_VEL:
            self.wesley_jump = False
            self.wesley_run = True
            self.jump_vel = self.JUMP_VEL

    def run(self):
        self.image = CORRENDO[self.step_index // 5]
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_index += 1

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(SCREEN, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)
        for obstacle in obstacles:
            pygame.draw.line(SCREEN, self.color, (self.rect.x + 54, self.rect.y + 12), obstacle.rect.center, 2)


class Obstacle:
    def __init__(self, image, number_of_cacti):
        self.image = image
        self.type = number_of_cacti
        self.rect = self.image[self.type].get_rect()
        self.rect.x = TELA_LARGURA

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 300


def remove(index):
    wesleys.pop(index)
    ge.pop(index)
    nets.pop(index)


def distance(pos_a, pos_b):
    dx = pos_a[0]-pos_b[0]
    dy = pos_a[1]-pos_b[1]
    return math.sqrt(dx**2+dy**2)


def eval_genomes(genomes, config):
    global game_speed, x_pos_bg, y_pos_bg, obstacles, wesleys, ge, nets, points
    clock = pygame.time.Clock()
    points = 0

    obstacles = []
    wesleys = []
    ge = []
    nets = []

    x_pos_bg = 0
    y_pos_bg = 380
    game_speed = 20

    for genome_id, genome in genomes:
        wesleys.append(Wesley())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        text = FONTE.render(f'Pontos:  {str(points)}', True, (0, 0, 0))
        TELA.blit(text, (950, 50))

    def statistics():
        global wesleys, game_speed, ge
        text_1 = FONTE.render(f'Wesleys vivos:  {str(len(wesleys))}', True, (0, 0, 0))
        text_2 = FONTE.render(f'Geração:  {pop.generation+1}', True, (0, 0, 0))
        text_3 = FONTE.render(f'Velocidade do jogo:  {str(game_speed)}', True, (0, 0, 0))

        TELA.blit(text_1, (50, 450))
        TELA.blit(text_2, (50, 480))
        TELA.blit(text_3, (50, 510))

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        TELA.blit(BG, (x_pos_bg, y_pos_bg))
        TELA.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        TELA.fill((255, 255, 255))

        for wesley in wesleys:
            wesley.update()
            wesley.draw(TELA)

        if len(wesleys) == 0:
            break

        if len(obstacles) == 0:
            rand_int = random.randint(0, 1)
            if rand_int == 0:
                obstacles.append(SmallCactus(CACTUS_PEQUENO, random.randint(0, 2)))
            elif rand_int == 1:
                obstacles.append(LargeCactus(CACTUS_GRANDE, random.randint(0, 2)))

        for obstacle in obstacles:
            obstacle.draw(TELA)
            obstacle.update()
            for i, wesley in enumerate(wesleys):
                if wesley.rect.colliderect(obstacle.rect):
                    ge[i].fitness -= 1
                    remove(i)

        for i, wesley in enumerate(wesleys):
            output = nets[i].activate((wesley.rect.y,
                                       distance((wesley.rect.x, wesley.rect.y),
                                        obstacle.rect.midtop)))
            if output[0] > 0.5 and wesley.rect.y == wesley.Y_POS:
                wesley.wesley_jump = True
                wesley.wesley_run = False

        statistics()
        score()
        background()
        clock.tick(30)
        pygame.display.update()


# Setup the NEAT Neural Network
def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    pop.run(eval_genomes, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
