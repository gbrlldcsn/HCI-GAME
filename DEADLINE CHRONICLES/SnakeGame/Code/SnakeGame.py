import pygame
import sys
import random
import math

# Colors (dark theme, spacetime-inspired)
BLACK = (10, 10, 20)
DARK_PURPLE = (40, 5, 65)
PURPLE = (120, 60, 180)
CYAN = (85, 214, 255)
WORMHOLE = (90, 0, 160)
STAR = (245, 245, 255)
DEFAULT_SNAKE_HEAD = (255, 90, 210)
DEFAULT_SNAKE_BODY = (140, 0, 160)
TIME_ORB = (0, 255, 200)
GRID_GLOW = (120, 30, 150, 35)  # RGBA for grid glow

# Some extra color choices for snake
SNAKE_COLORS = [
    {"name": "Pink", "head": (255, 90, 210), "body": (140, 0, 160)},
    {"name": "Blue", "head": (85, 214, 255), "body": (0, 120, 200)},
    {"name": "Gold", "head": (255, 221, 77), "body": (190, 150, 50)},
    {"name": "Green", "head": (60, 255, 120), "body": (40, 150, 80)},
    {"name": "Red", "head": (255, 51, 51), "body": (150, 20, 20)},
    {"name": "White", "head": (255, 255, 255), "body": (180, 180, 180)},
]

CELL_SIZE = 32
GRID_WIDTH = 40
GRID_HEIGHT = 22
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT
WINDOW_HEIGHT = 720

STARFIELD_DENSITY = 120

pygame.init()
screen = pygame.display.set_mode((WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Quantum Slither")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 28)
pygame.mixer.music.load("C:\\Users\\Gabrielle\\PycharmProjects\\\HCI\\DEADLINE CHRONICLES\\SnakeGame\\Audio\\background.wav")
pygame.mixer.music.play(-1)

PAUSE_ICON_X = 16
PAUSE_ICON_Y = 16
PAUSE_ICON_SIZE = 32
pause_area = pygame.Rect(PAUSE_ICON_X, PAUSE_ICON_Y, PAUSE_ICON_SIZE, PAUSE_ICON_SIZE)

def make_starfield():
    stars = []
    for _ in range(STARFIELD_DENSITY):
        px = random.randint(0, WIDTH - 1)
        py = random.randint(0, HEIGHT - 1)
        size = random.choice([1, 1, 2])
        color = (
            max(0, min(255, STAR[0] + random.randint(-10, 10))),
            max(0, min(255, STAR[1] + random.randint(-10, 10))),
            max(0, min(255, STAR[2] + random.randint(-10, 10)))
        )
        alpha = random.randint(180, 255)
        stars.append({"pos": (px, py), "size": size, "color": color, "alpha": alpha})
    return stars

starfield = make_starfield()

def draw_background(frame_count):
    screen.fill(BLACK)
    grid_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(grid_surf, GRID_GLOW, (x, 0), (x, HEIGHT), 5)
        pygame.draw.line(grid_surf, DARK_PURPLE, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(grid_surf, GRID_GLOW, (0, y), (WIDTH, y), 5)
        pygame.draw.line(grid_surf, DARK_PURPLE, (0, y), (WIDTH, y), 1)
    screen.blit(grid_surf, (0, 0))

    waves_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for i in range(4):
        phase = (frame_count / 28.0) + i * math.pi / 2
        cy = int(HEIGHT // 2 + math.sin(phase) * 130)
        color = (60, 0, 120, 25)
        pygame.draw.ellipse(waves_surf, color, (0, cy - 80, WIDTH, 180), 0)
    screen.blit(waves_surf, (0, 0))

    for s in starfield:
        star_color = s["color"]
        if len(star_color) != 3:
            star_color = STAR
        alpha = max(0, min(255, s["alpha"]))
        star = pygame.Surface((s["size"] * 2, s["size"] * 2), pygame.SRCALPHA)
        star.fill((0, 0, 0, 0))
        pygame.draw.circle(star, (star_color[0], star_color[1], star_color[2], alpha), (s["size"], s["size"]), s["size"])
        screen.blit(star, (s["pos"][0], s["pos"][1]))

    for _ in range(5):
        px = random.randint(0, WIDTH - 1)
        py = random.randint(0, HEIGHT - 1)
        color = (
            min(255, STAR[0] + random.randint(-15, 25)),
            min(255, STAR[1] + random.randint(-15, 25)),
            min(255, STAR[2] + random.randint(0, 25)),
            random.randint(180, 255)
        )
        pygame.draw.circle(screen, color, (px, py), 1)

MENU_BTN_W = 240
MENU_BTN_H = 60
MENU_BTN_COLOR = (40, 5, 65)
MENU_BTN_HOVER = (120, 60, 180)
MENU_BTN_TXT_COLOR = (255, 255, 255)
COLOR_BTN_W = 120
COLOR_BTN_H = 50

def draw_main_menu(frame_count, hover_idx=-1, color_hover_idx=-1, selected_color_idx=0):
    draw_background(frame_count)
    title_font = pygame.font.SysFont("consolas", 62)
    title_text = title_font.render("Quantum Slither", True, (255, 255, 255))
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 280))

    color_label_font = pygame.font.SysFont("consolas", 28)
    color_label = color_label_font.render("Choose Your Snake Color:", True, (255, 255, 255))
    screen.blit(color_label, (WIDTH//2 - color_label.get_width()//2, HEIGHT//2 - 170))

    color_btn_rects = []
    color_btn_start_x = WIDTH//2 - (len(SNAKE_COLORS)//2 * (COLOR_BTN_W + 10))
    for i, color in enumerate(SNAKE_COLORS):
        btn_rect = pygame.Rect(
            color_btn_start_x + i*(COLOR_BTN_W+10), HEIGHT//2 - 120, COLOR_BTN_W, COLOR_BTN_H
        )
        color_btn_rects.append(btn_rect)
        if i == selected_color_idx:
            pygame.draw.rect(screen, (255, 255, 255), btn_rect.inflate(8, 8), border_radius=16, width=4)
        btn_bg = MENU_BTN_HOVER if i == color_hover_idx else MENU_BTN_COLOR
        pygame.draw.rect(screen, btn_bg, btn_rect, border_radius=14)
        pygame.draw.rect(screen, color["head"], btn_rect.inflate(-20, -20), border_radius=10)
        btn_font = pygame.font.SysFont("consolas", 18)
        btn_txt = btn_font.render(color["name"], True, (0, 0, 0) if sum(color["head"]) > 450 else (255,255,255))
        screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2, btn_rect.centery - btn_txt.get_height()//2))

    btn_font = pygame.font.SysFont("consolas", 30)
    btns = ["Play", "Quit"]
    btn_rects = []
    for i, txt in enumerate(btns):
        rect = pygame.Rect(
            WIDTH//2 - MENU_BTN_W//2,
            HEIGHT//2 - 20 + (MENU_BTN_H + 30)*i,
            MENU_BTN_W,
            MENU_BTN_H)
        btn_rects.append(rect)
        color = MENU_BTN_HOVER if i == hover_idx else MENU_BTN_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=14)
        btn_txt = btn_font.render(txt, True, MENU_BTN_TXT_COLOR)
        screen.blit(btn_txt, (rect.centerx - btn_txt.get_width()//2, rect.centery - btn_txt.get_height()//2))
    return btn_rects, color_btn_rects

def show_main_menu():
    frame_count = 0
    hover_idx = -1
    color_hover_idx = -1
    selected_color_idx = 0
    while True:
        clock.tick(60)
        frame_count += 1
        mouse = pygame.mouse.get_pos()
        btn_rects, color_btn_rects = draw_main_menu(frame_count, hover_idx, color_hover_idx, selected_color_idx)
        pygame.display.flip()
        hover_idx = -1
        color_hover_idx = -1
        for i, rect in enumerate(btn_rects):
            if rect.collidepoint(mouse):
                hover_idx = i
        for i, rect in enumerate(color_btn_rects):
            if rect.collidepoint(mouse):
                color_hover_idx = i
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(color_btn_rects):
                    if rect.collidepoint(event.pos):
                        selected_color_idx = i
                        break
                for i, rect in enumerate(btn_rects):
                    if rect.collidepoint(event.pos):
                        if i == 0:
                            return selected_color_idx
                        elif i == 1:
                            pygame.quit()
                            sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def draw_home_screen(frame_count):
    draw_background(frame_count)
    title_font = pygame.font.SysFont("consolas", 48)
    title_text = title_font.render("SNAKE GAME", True, (255, 255, 255))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 150))
    subtitle_font = pygame.font.SysFont("consolas", 24)
    subtitle_text = subtitle_font.render("BEAT THIS GAME", True, CYAN)
    screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, HEIGHT // 2 - 90))
    pygame.draw.line(screen, PURPLE, (WIDTH // 2 - 100, HEIGHT // 2 - 50), (WIDTH // 2 + 100, HEIGHT // 2 - 50), 2)
    prompt_font = pygame.font.SysFont("consolas", 32)
    prompt_text = prompt_font.render("PLEASE CLICK ANY KEY TO START!", True, (200, 140, 255))
    screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2))
    controls_font = pygame.font.SysFont("consolas", 28)
    controls_text = controls_font.render("CONTROLS", True, (255, 255, 255))
    screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, HEIGHT // 2 + 80))
    arrows_font = pygame.font.SysFont("consolas", 15)
    arrows_text = arrows_font.render("ARROW DOWN, UP, LEFT, RIGHT OR W, S, A, D", True, (180, 180, 180))
    screen.blit(arrows_text, (WIDTH//2 - arrows_text.get_width()//2, HEIGHT//2 + 120))

def show_home_screen():
    frame_count = 0
    waiting = True
    while waiting:
        clock.tick(60)
        frame_count += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
        draw_home_screen(frame_count)
        pygame.display.flip()

def random_pos(snake):
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in snake:
            return pos

def draw_snake(snake, snake_head_color, snake_body_color):
    for i, pos in enumerate(snake):
        color = snake_head_color if i == 0 else snake_body_color
        x, y = pos[0] * CELL_SIZE, pos[1] * CELL_SIZE
        pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE), border_radius=8)
        if i == 0:
            for r in range(18, CELL_SIZE - 5, 2):
                pygame.draw.circle(screen, WORMHOLE, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), r, 1)

def draw_food_cube(pos, frame_count=0):
    x, y = pos[0] * CELL_SIZE + CELL_SIZE // 2, pos[1] * CELL_SIZE + CELL_SIZE // 2
    glow_color = (0, 255, 200, 70)
    for r in range(CELL_SIZE//2, CELL_SIZE//2+12, 3):
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, glow_color, (CELL_SIZE//2 - r//2, CELL_SIZE//2 - r//2, r, r), border_radius=8)
        screen.blit(surf, (x - CELL_SIZE//2, y - CELL_SIZE//2))
    angle = (frame_count % 60) * 6
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(surf, (0, 255, 200), (8, 8, CELL_SIZE-16, CELL_SIZE-16), border_radius=8)
    surf = pygame.transform.rotate(surf, angle)
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect.topleft)
    for i in range(3):
        theta = angle + 120*i
        ex = int(x + math.cos(math.radians(theta)) * (CELL_SIZE//2+3))
        ey = int(y + math.sin(math.radians(theta)) * (CELL_SIZE//2+3))
        pygame.draw.circle(screen, CYAN, (ex, ey), 5)

def draw_food_starcore(pos, frame_count=0):
    x, y = pos[0] * CELL_SIZE + CELL_SIZE // 2, pos[1] * CELL_SIZE + CELL_SIZE // 2
    pulse = 2 + int(2 * math.sin(frame_count * 0.15))
    pygame.draw.circle(screen, (255, 255, 200), (x, y), CELL_SIZE // 2 - 2 + pulse)
    pygame.draw.circle(screen, (255, 160, 80), (x, y), (CELL_SIZE // 3) + pulse)
    for i in range(8):
        angle = frame_count * 0.2 + i * math.pi / 4
        dx = int(math.cos(angle) * (CELL_SIZE//2 + 1 + pulse*1.3))
        dy = int(math.sin(angle) * (CELL_SIZE//2 + 1 + pulse*1.3))
        pygame.draw.line(screen, CYAN, (x, y), (x+dx, y+dy), 2)

def draw_food_crystal(pos, frame_count=0):
    x, y = pos[0] * CELL_SIZE + CELL_SIZE // 2, pos[1] * CELL_SIZE + CELL_SIZE // 2
    color1 = (0, 255, 200)
    color2 = (120, 60, 180)
    t = (math.sin(frame_count * 0.12) + 1) / 2
    r = int(color1[0]*t + color2[0]*(1-t))
    g = int(color1[1]*t + color2[1]*(1-t))
    b = int(color1[2]*t + color2[2]*(1-t))
    points = [
        (x, y - CELL_SIZE//2 + 4),
        (x + CELL_SIZE//2 - 4, y),
        (x, y + CELL_SIZE//2 - 4),
        (x - CELL_SIZE//2 + 4, y),
    ]
    pygame.draw.polygon(screen, (r, g, b), points)
    pygame.draw.polygon(screen, PURPLE, points, 2)
    for i in range(4):
        px, py = points[i]
        px2, py2 = x, y
        pygame.draw.line(screen, CYAN, (px, py), (px2, py2), 1)

food_styles = [draw_food_cube, draw_food_starcore, draw_food_crystal]

def draw_congratulations(score):
    congrats_txt = font.render("CONGRATULATIONS!!", True, (0, 255, 200))
    passed_txt = font.render("You passed this level", True, CYAN)
    screen.blit(congrats_txt, (WIDTH // 2 - congrats_txt.get_width() // 2, HEIGHT // 2 - 110))
    screen.blit(passed_txt, (WIDTH // 2 - passed_txt.get_width() // 2, HEIGHT // 2 - 65))
    prompt_txt = font.render("You can now proceed to Level 3", True, (200, 140, 255))
    screen.blit(prompt_txt, (WIDTH // 2 - prompt_txt.get_width() // 2, HEIGHT // 2 - 30))
    score_txt = font.render(f"Score: {score}/15", True, PURPLE)
    screen.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, HEIGHT // 2 + 20))

def draw_game_over(score):
    over_txt = font.render("Game Over!", True, (255, 120, 180))
    screen.blit(over_txt, (WIDTH // 2 - over_txt.get_width() // 2, HEIGHT // 2 - 80))
    prompt_txt = font.render("Press any key to restart", True, (200, 140, 255))
    screen.blit(prompt_txt, (WIDTH // 2 - prompt_txt.get_width() // 2, HEIGHT // 2 - 30))
    score_txt = font.render(f"Score: {score}/15", True, PURPLE)
    screen.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, HEIGHT // 2 + 20))

def draw_pause_symbol(surface, x=16, y=16, size=32, hover=False):
    color_bg = (60, 20, 80) if not hover else (120, 60, 180)
    pygame.draw.circle(surface, color_bg, (x + size//2, y + size//2), size//2)
    bar_color = (85, 214, 255)
    bar_w = size // 6
    bar_h = size // 2
    bar_spacing = size // 4
    top = y + (size - bar_h)//2
    left1 = x + size//2 - bar_spacing//2 - bar_w
    left2 = x + size//2 + bar_spacing//2
    pygame.draw.rect(surface, bar_color, (left1, top, bar_w, bar_h), border_radius=4)
    pygame.draw.rect(surface, bar_color, (left2, top, bar_w, bar_h), border_radius=4)

def draw_pause_overlay(frame_count, hover_idx=-1):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 155))
    screen.blit(overlay, (0, 0))
    pause_font = pygame.font.SysFont("consolas", 52)
    txt = pause_font.render("PAUSED", True, CYAN)
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 140))

    btn_font = pygame.font.SysFont("consolas", 30)
    btns = ["Resume", "Main Menu"]
    btn_rects = []
    for i, txtb in enumerate(btns):
        rect = pygame.Rect(WIDTH//2 - MENU_BTN_W//2,
                           HEIGHT//2 - 10 + (MENU_BTN_H + 30)*i,
                           MENU_BTN_W, MENU_BTN_H)
        btn_rects.append(rect)
        color = MENU_BTN_HOVER if i == hover_idx else MENU_BTN_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=14)
        btn_txt = btn_font.render(txtb, True, MENU_BTN_TXT_COLOR)
        screen.blit(btn_txt, (rect.centerx - btn_txt.get_width()//2, rect.centery - btn_txt.get_height()//2))
    return btn_rects

def pause_menu(frame_count):
    hover_idx = -1
    while True:
        clock.tick(60)
        mouse = pygame.mouse.get_pos()
        btn_rects = draw_pause_overlay(frame_count, hover_idx)
        pygame.display.flip()
        hover_idx = -1
        for i, rect in enumerate(btn_rects):
            if rect.collidepoint(mouse):
                hover_idx = i
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(btn_rects):
                    if rect.collidepoint(event.pos):
                        return i
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 0

def main():
    while True:
        selected_color_idx = show_main_menu()
        snake_colors = SNAKE_COLORS[selected_color_idx]
        snake_head_color = snake_colors["head"]
        snake_body_color = snake_colors["body"]
        show_home_screen()
        frame_count = 0
        while True:
            # snake with two blocks so it won't instantly collide with itself
            snake = [
                (GRID_WIDTH // 2, GRID_HEIGHT // 2),
                (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2)
            ]
            direction = (1, 0)
            next_direction = direction  # For key buffering/fair movement
            food = random_pos(snake)
            food_style = random.choice(food_styles)
            score = 0
            speed = 6
            speed_increase = 0.25
            max_speed = 18
            move_timer = 0
            gameover = False
            congratulations = False
            paused = False

            while not gameover:
                clock.tick(60)
                frame_count += 1
                move_timer += 1
                mouse = pygame.mouse.get_pos()
                hovering = pause_area.collidepoint(mouse)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            paused = True
                        elif event.key in [pygame.K_UP, pygame.K_w]:
                            if direction != (0, 1) and next_direction != (0, -1):
                                next_direction = (0, -1)
                        elif event.key in [pygame.K_DOWN, pygame.K_s]:
                            if direction != (0, -1) and next_direction != (0, 1):
                                next_direction = (0, 1)
                        elif event.key in [pygame.K_LEFT, pygame.K_a]:
                            if direction != (1, 0) and next_direction != (-1, 0):
                                next_direction = (-1, 0)
                        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                            if direction != (-1, 0) and next_direction != (1, 0):
                                next_direction = (1, 0)
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if pause_area.collidepoint(event.pos):
                            paused = True

                if paused:
                    res = pause_menu(frame_count)
                    if res == 0:
                        paused = False
                        continue
                    elif res == 1:
                        break

                if move_timer >= (60 // speed):
                    move_timer = 0
                    direction = next_direction  # Safe to change direction only per frame
                    new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
                    if (new_head in snake) or not (0 <= new_head[0] < GRID_WIDTH) or not (0 <= new_head[1] < GRID_HEIGHT):
                        gameover = True
                    else:
                        snake.insert(0, new_head)
                        if new_head == food:
                            score += 1
                            speed = min(max_speed, speed + speed_increase)
                            if score >= 15:
                                gameover = True
                                congratulations = True
                            else:
                                food = random_pos(snake)
                                food_style = random.choice(food_styles)
                        else:
                            snake.pop()

                draw_background(frame_count)
                food_style(food, frame_count)
                draw_snake(snake, snake_head_color, snake_body_color)
                score_txt = font.render(f"{score}/15", True, PURPLE)
                screen.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, 10))
                draw_pause_symbol(screen, PAUSE_ICON_X, PAUSE_ICON_Y, PAUSE_ICON_SIZE, hover=hovering)
                pygame.display.flip()

            draw_background(frame_count)
            food_style(food, frame_count)
            draw_snake(snake, snake_head_color, snake_body_color)
            if congratulations:
                draw_congratulations(score)
            else:
                draw_game_over(score)
            pygame.display.flip()

            waiting = True
            while waiting:
                clock.tick(12)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                        waiting = False
            break

if __name__ == "__main__":
    main()

