import pygame
import os
import random
pygame.init()
from pygame import mixer

# Global Constants
SCREEN_HEIGHT = 720
SCREEN_WIDTH = 1280
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "JackRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "JackRun2.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))
BG = pygame.image.load(os.path.join("Assets/Other", "grass.png"))

JUMP_SFX = pygame.mixer.Sound(os.path.join("Assets/sounds", "jump.wav"))
JUMP_SFX.set_volume(0.5)

DEATH_SFX = pygame.mixer.Sound(os.path.join("Assets/sounds", "die.wav"))
DEATH_SFX.set_volume(0.5)


BG_MUSIC = mixer.music.load(os.path.join("Assets/sounds", "his_theme.mp3"))
pygame.mixer.music.set_volume(0.1)
mixer.music.play(-1)

class Dinosaur:
    X_POS = 80
    Y_POS = 335
    Y_POS_DUCK = 335
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING
        self.jump_sfx = JUMP_SFX

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.hitbox = pygame.Rect(self.dino_rect.x + 12, self.dino_rect.y + 10, 40, 50)

    def update(self, userInput):

        if self.dino_duck:
            self.duck()
        elif self.dino_run:
            self.run()
        elif self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
            self.jump_sfx.play()

        if userInput[pygame.K_SPACE] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
            self.jump_sfx.play()

        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False

        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.hitbox = pygame.Rect(self.dino_rect.x + 12, self.dino_rect.y + 30, 30, 40)
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.hitbox = pygame.Rect(self.dino_rect.x + 12, self.dino_rect.y + 9, 30, 40)
        self.step_index += 1

    def jump(self):
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 1

        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

        self.hitbox = pygame.Rect(self.dino_rect.x + 12, self.dino_rect.y + 10, 33, 30)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))
        pygame.draw.rect(SCREEN, (255, 0, 0), self.hitbox, 2)

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Background:
    def __init__(self):


        self.image = pygame.image.load(os.path.join("Assets/BG", "test.png"))


        self.image_width = self.image.get_width()
        self.x1 = 0
        self.x2 = self.image_width
        self.y = 5

    def update(self):
        self.x1 -= game_speed // 4
        self.x2 -= game_speed // 4
        if self.x1 <= -self.image_width:
            self.x1 = self.x2 + self.image_width
        if self.x2 <= -self.image_width:
            self.x2 = self.x1 + self.image_width

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x1, self.y))
        SCREEN.blit(self.image, (self.x2, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH
        self.hitbox = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width - 10, self.rect.height - 10)

    def update(self):
        self.rect.x -= game_speed
        self.hitbox.x = self.rect.x + 5
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)
        pygame.draw.rect(SCREEN, (255, 0, 0), self.hitbox, 2)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 350
        self.hitbox = pygame.Rect(self.rect.x + 100, self.rect.y + 5, self.rect.width - 15, self.rect.height - 10)


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 330
        self.hitbox = pygame.Rect(self.rect.x + 100, self.rect.y + 5, self.rect.width - 10, self.rect.height - 10)


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 280
        self.index = 0
        self.hitbox = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width - 8, self.rect.height - 8)

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        pygame.draw.rect(SCREEN, (255, 0, 0), self.hitbox, 2)
        self.index += 1

class Coin:
    def __init__(self, obstacle):
        self.image = pygame.image.load(os.path.join("Assets/BG", "bulb.png"))
        self.rect = self.image.get_rect()

        # Position the coin relative to obstacle
        self.rect.x = obstacle.rect.x + obstacle.rect.width // 2 - self.image.get_width() // 2

        # Randomly choose to place on top or below
        if random.choice([True, False]):
            self.rect.y = obstacle.rect.y - self.image.get_height() - 20 # on top
        else:
            self.rect.y = obstacle.rect.y + obstacle.rect.height + 10    # underneath

        self.collected = False

    def update(self):
        self.rect.x -= game_speed

    def draw(self, screen):
        if not self.collected:
            screen.blit(self.image, self.rect)
            pygame.draw.rect(screen, (255, 215, 0), self.rect, 1)  # optional: outline



def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    background_img = Background()
    points = 0
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    font = pygame.font.Font('freesansbold.ttf', 20)
    obstacles = []
    death_count = 0
    coins = []
    collected_coins = 0
    next_coin_spawn_score = 1000
    death_sfx = DEATH_SFX

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        text = font.render("Points: " + str(points), True, (0, 0, 0))
        coin_text = font.render("Coins: " + str(collected_coins), True, (255, 215, 0))
        SCREEN.blit(coin_text, (1000, 70))
        SCREEN.blit(text, (1000, 40))

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        background_img.draw(SCREEN)
        background_img.update()
        background()

        player.draw(SCREEN)
        player.update(userInput)

        if len(obstacles) == 0:
            choice = random.randint(0, 2)
            if choice == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif choice == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            else:
                obstacles.append(Bird(BIRD))

        if points >= next_coin_spawn_score and collected_coins < 999:
            if obstacles:
                obstacle = random.choice(obstacles)
                coin = Coin(obstacle)
                coins.append(coin)
                next_coin_spawn_score += 100


        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.hitbox.colliderect(obstacle.hitbox):
                death_sfx.play()
                pygame.time.delay(1000)
                death_count += 1
                menu(death_count)


        for coin in coins:
            coin.update()
            coin.draw(SCREEN)
            if not coin.collected and player.dino_rect.colliderect(coin.rect):
                coin.collected = True
                collected_coins += 1

        cloud.draw(SCREEN)
        cloud.update()
        score()

        clock.tick(30)
        pygame.display.update()


def menu(death_count):
    global points
    run = True
    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font('freesansbold.ttf', 30)

        if death_count == 0:
            text = font.render("Press any Key to Start", True, (0, 0, 0))
        else:
            text = font.render("Press any Key to Restart", True, (0, 0, 0))
            score = font.render("Your Score: " + str(points), True, (0, 0, 0))
            SCREEN.blit(score, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50))

        SCREEN.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.KEYDOWN:
                main()


menu(death_count=0)
