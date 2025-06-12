import pygame
import sys
import os
import random
import math

# Initialize pygame
pygame.init()

# Display constants
WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Deadline Chronicles")

# Set window icon
try:
    icon = pygame.image.load("Images\\DEADLINE_CHRONICLES.png")
    pygame.display.set_icon(icon)
except pygame.error:
    print("Warning: Could not load icon image")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
BEIGE = (245, 215, 160)  # Color for pixel text
BUTTON_RED = (180, 60, 40)  # Main button color
BUTTON_RED_DARK = (140, 30, 20)  # Dark red for shadows/borders
BUTTON_RED_LIGHT = (220, 80, 60)  # Light red for highlights
DARK_BLUE = (30, 30, 80)  # Game background color

# Matrix Rain Colors
MATRIX_RED_LIGHT = (0xeb, 0x88, 0x79)
MATRIX_BLUE_LIGHT = (0x8c, 0xd7, 0xec)
MATRIX_BLUE_DARK = (0x4a, 0x8f, 0xb5)
MATRIX_RED_DARK = (0xaa, 0x44, 0x44)
MATRIX_COLORS = [MATRIX_RED_LIGHT, MATRIX_BLUE_LIGHT, MATRIX_BLUE_DARK, MATRIX_RED_DARK]

# Pixel Fonts
FONT_DIR = os.path.join(os.path.dirname(__file__), "Assets", "font", "PixelFonts")
FONT_REGULAR = os.path.join(FONT_DIR, "slkscr.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "slkscrb.ttf")
FONT_EXTENDED = os.path.join(FONT_DIR, "slkscre.ttf")
FONT_EXTENDED_BOLD = os.path.join(FONT_DIR, "slkscreb.ttf")

# Load pixel fonts
try:
    font_small = pygame.font.Font(FONT_REGULAR, 24)
    font_medium = pygame.font.Font(FONT_REGULAR, 48)
    font_large = pygame.font.Font(FONT_REGULAR, 72)

    font_small_bold = pygame.font.Font(FONT_BOLD, 24)
    font_medium_bold = pygame.font.Font(FONT_BOLD, 48)
    font_large_bold = pygame.font.Font(FONT_BOLD, 72)

    font_small_extended = pygame.font.Font(FONT_EXTENDED, 24)
    font_medium_extended = pygame.font.Font(FONT_EXTENDED, 48)
    font_large_extended = pygame.font.Font(FONT_EXTENDED, 72)

    font_small_extended_bold = pygame.font.Font(FONT_EXTENDED_BOLD, 24)
    font_medium_extended_bold = pygame.font.Font(FONT_EXTENDED_BOLD, 48)
    font_large_extended_bold = pygame.font.Font(FONT_EXTENDED_BOLD, 72)

    pixel_fonts_loaded = True
except pygame.error:
    print("Warning: Could not load pixel fonts, falling back to system fonts")
    font_small = pygame.font.SysFont("Arial", 24)
    font_medium = pygame.font.SysFont("Arial", 48)
    font_large = pygame.font.SysFont("Arial", 72)
    pixel_fonts_loaded = False

# Load logo image
try:
    logo_img = pygame.image.load('Images\\DEADLINE_CHRONICLES.png')
    logo_img = pygame.transform.scale(logo_img, (580, 300))
except pygame.error:
    print("Warning: Could not load logo image 'Images\\DEADLINE_CHRONICLES.png'")
    logo_img = None

# Matrix Rain Setup
if pixel_fonts_loaded:
    matrix_font = pygame.font.Font(FONT_REGULAR, 20)
else:
    matrix_font = pygame.font.SysFont("Consolas", 20)

MATRIX_FONT_HEIGHT = matrix_font.get_height()
if matrix_font.size('W')[0] > 0:
    NUM_COLUMNS = WIDTH // matrix_font.size('W')[0]
else:
    NUM_COLUMNS = WIDTH // 20

matrix_streams = []

class MatrixStream:
    def __init__(self, x, screen_height, font, colors):
        self.x = x
        self.y = random.randint(-screen_height, 0)
        self.speed = random.randint(3, 7)
        self.length = random.randint(10, 30)
        self.characters = []
        self.font = font
        self.colors = colors
        self.screen_height = screen_height
        self.init_characters()

    def init_characters(self):
        self.characters = []
        for _ in range(self.length):
            char = chr(random.randint(33, 126))
            color = random.choice(self.colors)
            self.characters.append({"char": char, "color": color})

    def update(self):
        self.y += self.speed
        for i in range(self.length):
            self.characters[i]["char"] = chr(random.randint(33, 126))
        if self.y > self.screen_height:
            self.y = random.randint(-self.screen_height, 0) - (self.length * MATRIX_FONT_HEIGHT)
            self.speed = random.randint(3, 7)
            self.length = random.randint(10, 30)
            self.init_characters()

    def draw(self, surface):
        current_y = self.y
        for i, char_data in enumerate(self.characters):
            char_surface = self.font.render(char_data["char"], True, char_data["color"])
            alpha_stream_fade = 255 - int(255 * (i / self.length))
            alpha_stream_fade = max(0, min(255, alpha_stream_fade))
            absolute_char_y = current_y
            alpha_screen_y = int(50 + (205 * (absolute_char_y / self.screen_height)))
            alpha_screen_y = max(50, min(255, alpha_screen_y))
            final_alpha = min(alpha_stream_fade, alpha_screen_y)
            char_surface.set_alpha(final_alpha)
            surface.blit(char_surface, (self.x, current_y))
            current_y += MATRIX_FONT_HEIGHT

for i in range(NUM_COLUMNS):
    x_pos = i * matrix_font.size('W')[0]
    matrix_streams.append(MatrixStream(x_pos, HEIGHT, matrix_font, MATRIX_COLORS))

class PixelButton:
    def __init__(self, x, y, width, height, text, image_path=None, animation_base_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.is_clicked = False
        self.pixel_size = 5
        self.shadow_offset = 4
        self.image_path = image_path
        self.button_image = None

        self.animation_base_path = animation_base_path
        self.idle_frames = []
        self.hover_frames = []
        self.click_frames = []
        self.current_frame_index = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        self.current_state = "idle"

        if animation_base_path:
            self.load_animations()
        elif image_path:
            try:
                self.button_image = pygame.image.load(image_path)
                self.button_image = pygame.transform.scale(self.button_image, (width, height))
            except pygame.error:
                print(f"Warning: Could not load button image '{image_path}'")
                self.button_image = None

        if not self.button_image and not animation_base_path:
            if pixel_fonts_loaded:
                font = font_small
            else:
                font = pygame.font.SysFont("Arial", 24)
            self.text_surface = font.render(text, True, BEIGE)
        else:
            self.text_surface = None

    def load_animations(self):
        idle_path = os.path.join(self.animation_base_path, "Idle")
        hover_path = os.path.join(self.animation_base_path, "Hover")
        click_path = os.path.join(self.animation_base_path, "Click")

        if "Start" in self.animation_base_path:
            for i in range(1, 5):
                try:
                    idle_img = pygame.image.load(os.path.join(idle_path, f"MainStartButtonTrueIdle{i}.png"))
                    idle_img = pygame.transform.scale(idle_img, (self.rect.width, self.rect.height))
                    self.idle_frames.append(idle_img)

                    hover_img = pygame.image.load(os.path.join(hover_path, f"MainStartButtonTrueHover{i}.png"))
                    hover_img = pygame.transform.scale(hover_img, (self.rect.width, self.rect.height))
                    self.hover_frames.append(hover_img)
                except pygame.error as e:
                    print(f"Warning: Could not load animation frame: {e}")

            for i in range(1, 5):
                try:
                    click_img = pygame.image.load(os.path.join(click_path, f"MainStartButtonTrueClick{i}.png"))
                    click_img = pygame.transform.scale(click_img, (self.rect.width, self.rect.height))
                    self.click_frames.append(click_img)
                except pygame.error as e:
                    print(f"Warning: Could not load animation frame: {e}")
        else:
            for i in range(1, 77):
                try:
                    idle_img = pygame.image.load(os.path.join(idle_path, f"ExitPngIdle{i}.png"))
                    idle_img = pygame.transform.scale(idle_img, (self.rect.width, self.rect.height))
                    self.idle_frames.append(idle_img)
                except pygame.error:
                    break

            for i in range(1, 77):
                try:
                    hover_img = pygame.image.load(os.path.join(hover_path, f"ExitPngHover{i}.png"))
                    hover_img = pygame.transform.scale(hover_img, (self.rect.width, self.rect.height))
                    self.hover_frames.append(hover_img)
                except pygame.error:
                    break

            for i in range(1, 77):
                try:
                    click_img = pygame.image.load(os.path.join(click_path, f"ExitPngClick{i}.png"))
                    click_img = pygame.transform.scale(click_img, (self.rect.width, self.rect.height))
                    self.click_frames.append(click_img)
                except pygame.error:
                    break

        if not self.idle_frames and not self.hover_frames and not self.click_frames:
            print(f"Warning: Could not load any animation frames from {self.animation_base_path}")
            if self.image_path:
                try:
                    self.button_image = pygame.image.load(self.image_path)
                    self.button_image = pygame.transform.scale(self.button_image, (self.rect.width, self.rect.height))
                except pygame.error:
                    print(f"Warning: Could not load fallback button image '{self.image_path}'")
                    self.button_image = None

    def update_animation(self, dt=1 / 60):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            frames = []
            if self.current_state == "idle":
                frames = self.idle_frames
            elif self.current_state == "hover":
                frames = self.hover_frames
            elif self.current_state == "click":
                frames = self.click_frames
            if frames:
                self.current_frame_index = (self.current_frame_index + 1) % len(frames)

    def draw(self, surface):
        if self.animation_base_path and self.idle_frames:
            if self.is_clicked and self.click_frames:
                self.current_state = "click"
            elif self.is_hovered and self.hover_frames:
                self.current_state = "hover"
            else:
                self.current_state = "idle"

            current_frame = None
            if self.current_state == "idle":
                current_frame = self.idle_frames[self.current_frame_index % len(self.idle_frames)]
            elif self.current_state == "hover":
                current_frame = self.hover_frames[self.current_frame_index % len(self.hover_frames)]
            elif self.current_state == "click":
                current_frame = self.click_frames[self.current_frame_index % len(self.click_frames)]

            if current_frame:
                image_rect = current_frame.get_rect(center=self.rect.center)
                surface.blit(current_frame, image_rect)
                return

        if self.button_image:
            offset = 2 if self.is_hovered else 0
            image_rect = self.button_image.get_rect(center=(self.rect.centerx + offset, self.rect.centery + offset))
            surface.blit(self.button_image, image_rect)
            return

        shadow_rect = pygame.Rect(self.rect.x + self.shadow_offset, self.rect.y + self.shadow_offset,
                                  self.rect.width, self.rect.height)
        pygame.draw.rect(surface, BUTTON_RED_DARK, shadow_rect)
        pygame.draw.rect(surface, BUTTON_RED, self.rect)
        pygame.draw.rect(surface, BUTTON_RED_LIGHT, (self.rect.x, self.rect.y, self.rect.width, self.pixel_size))
        pygame.draw.rect(surface, BUTTON_RED_LIGHT, (self.rect.x, self.rect.y, self.pixel_size, self.rect.height))
        pygame.draw.rect(surface, BUTTON_RED_DARK,
                         (self.rect.x, self.rect.y + self.rect.height - self.pixel_size, self.rect.width,
                          self.pixel_size))
        pygame.draw.rect(surface, BUTTON_RED_DARK,
                         (self.rect.x + self.rect.width - self.pixel_size, self.rect.y, self.pixel_size,
                          self.rect.height))
        if self.is_hovered:
            pygame.draw.rect(surface, WHITE, (self.rect.x, self.rect.y, self.rect.width, self.pixel_size))
            pygame.draw.rect(surface, WHITE, (self.rect.x, self.rect.y, self.pixel_size, self.rect.height))
        if self.text_surface:
            text_rect = self.text_surface.get_rect(center=self.rect.center)
            surface.blit(self.text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        if not self.is_hovered:
            self.is_clicked = False
        return self.is_hovered

    def handle_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            self.is_clicked = True
            return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_clicked = False
        return False


def draw_menu():
    SCREEN.fill(BLACK)
    for stream in matrix_streams:
        stream.update()
        stream.draw(SCREEN)
    if logo_img is not None:
        logo_rect = logo_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        SCREEN.blit(logo_img, logo_rect)
    else:
        title_text = font_large.render("Deadline Chronicles", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        SCREEN.blit(title_text, title_rect)
    start_button.draw(SCREEN)
    exit_button.draw(SCREEN)


def draw_game():
    SCREEN.fill(BLACK)
    for stream in matrix_streams:
        stream.update()
        stream.draw(SCREEN)
    back_button.draw(SCREEN)


def story_screen():
    clock = pygame.time.Clock()
    running = True
    if pixel_fonts_loaded:
        story_font = pygame.font.Font(FONT_REGULAR, 28)
        continue_font = pygame.font.Font(FONT_REGULAR, 20)
    else:
        story_font = pygame.font.SysFont("Arial", 28)
        continue_font = pygame.font.SysFont("Arial", 20)

    story_text = (
        "There was a student who was given a task by his professor to do a project, "
        "but he ended up in another dimension the \"DEV REALM\". Let's follow the student's journey."
    )
    words = story_text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        if story_font.size(test_line)[0] > WIDTH - 100:
            lines.append(' '.join(current_line))
            current_line = [word]
        else:
            current_line.append(word)
    if current_line:
        lines.append(' '.join(current_line))

    typing_speed = 0.05
    typing_timer = 0
    displayed_chars = [0] * len(lines)
    animation_complete = False
    continue_text = continue_font.render("Press any key to continue...", True, WHITE)
    show_continue = False

    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if animation_complete:
                    from Introduction import show_introduction
                    show_introduction(SCREEN, clock)
                    return
                else:
                    for i in range(len(lines)):
                        displayed_chars[i] = len(lines[i])
                    animation_complete = True
                    show_continue = True

        if not animation_complete:
            typing_timer += dt
            if typing_timer >= typing_speed:
                typing_timer = 0
                current_line_index = 0
                while current_line_index < len(lines) and displayed_chars[current_line_index] >= len(
                        lines[current_line_index]):
                    current_line_index += 1
                if current_line_index < len(lines):
                    displayed_chars[current_line_index] += 1
                    if displayed_chars[current_line_index] >= len(lines[current_line_index]):
                        if current_line_index == len(lines) - 1:
                            animation_complete = True
                            show_continue = True

        SCREEN.fill(BLACK)
        line_spacing = 10
        total_height = sum(story_font.size(line[:chars])[1] for line, chars in zip(lines, displayed_chars)) + line_spacing * (len(lines) - 1)
        start_y = (HEIGHT - total_height) // 2
        current_y = start_y
        for i, line in enumerate(lines):
            visible_text = line[:displayed_chars[i]]
            if visible_text:
                text_surface = story_font.render(visible_text, True, WHITE)
                text_rect = text_surface.get_rect(center=(WIDTH // 2, current_y))
                SCREEN.blit(text_surface, text_rect)
            current_y += story_font.size(line)[1] + line_spacing
        if show_continue:
            continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            SCREEN.blit(continue_text, continue_rect)
        pygame.display.flip()


def introduction_main():
    """Display Harold sprites and welcome message."""
    SCREEN.fill((0, 0, 0))
    try:
        harold_1 = pygame.image.load("Images\\SPRITES\\CHARACTER_SPRITES\\HAROLD\\HAROLD_1.png")
        harold_2 = pygame.image.load("Images\\SPRITES\\CHARACTER_SPRITES\\HAROLD\\HAROLD_2.png")
        harold_3 = pygame.image.load("Images\\SPRITES\\CHARACTER_SPRITES\\HAROLD\\HAROLD_3.png")
        harold_4 = pygame.image.load("Images\\SPRITES\\CHARACTER_SPRITES\\HAROLD\\HAROLD_4.png")
    except pygame.error as e:
        print(f"Error loading Harold images: {e}")
        return

    # Display each sprite briefly
    sprites = [harold_1, harold_2, harold_3, harold_4]
    for sprite in sprites:
        scaled_sprite = pygame.transform.scale(sprite, (200, 200))
        rect = scaled_sprite.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        SCREEN.fill((0, 0, 0))
        SCREEN.blit(scaled_sprite, rect)
        pygame.display.flip()
        pygame.time.delay(500)

    # Final welcome message
    font = pygame.font.SysFont(None, 64)
    text = font.render("Welcome to Deadline Chronicles!", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    SCREEN.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)


def game_loop():
    clock = pygame.time.Clock()
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            if back_button.handle_click(event):
                return
        back_button.check_hover(mouse_pos)
        draw_game()
        pygame.display.flip()
        clock.tick(60)


def shutdown_animation():
    clock = pygame.time.Clock()
    running = True
    animation_duration = 2.0
    current_time = 0
    if pixel_fonts_loaded:
        shutdown_font = pygame.font.Font(FONT_REGULAR, 60)
    else:
        shutdown_font = pygame.font.SysFont("Arial", 60)
    text_alpha = 0
    fade_alpha = 0
    flicker_speed = 6
    flicker_intensity = 0.3
    shake_intensity = 3

    while running and current_time < animation_duration:
        dt = clock.tick(60) / 1000
        current_time += dt
        progress = current_time / animation_duration

        if progress < 0.3:
            text_alpha = int(255 * (progress / 0.3))
        else:
            text_alpha = 255

        if progress > 0.7:
            fade_progress = (progress - 0.7) / 0.3
            fade_alpha = int(255 * fade_progress)

        if progress <= 0.7:
            flicker_value = math.sin(progress * flicker_speed * math.pi * 2)
            flicker_factor = (flicker_value + 1) / 2
            flicker_factor = flicker_factor * flicker_intensity
            color_value = int(255 * flicker_factor)
            background_color = (color_value, color_value, color_value)
            SCREEN.fill(background_color)
        else:
            SCREEN.fill(BLACK)

        pulse_factor = 1.0 + 0.05 * math.sin(progress * 15)
        if pixel_fonts_loaded:
            pulse_size = int(60 * pulse_factor)
            pulse_font = pygame.font.Font(FONT_BOLD, pulse_size)
        else:
            pulse_size = int(60 * pulse_factor)
            pulse_font = pygame.font.SysFont("Arial", pulse_size)

        pulse_text = pulse_font.render("SHUTTING DOWN", True, WHITE if progress <= 0.7 else WHITE)
        pulse_text.set_alpha(text_alpha)
        shake_offset_x = random.randint(-shake_intensity, shake_intensity)
        shake_offset_y = random.randint(-shake_intensity, shake_intensity)
        pulse_rect = pulse_text.get_rect(center=(WIDTH // 2 + shake_offset_x, HEIGHT // 2 + shake_offset_y))
        SCREEN.blit(pulse_text, pulse_rect)

        if fade_alpha > 0:
            fade_surface = pygame.Surface((WIDTH, HEIGHT))
            fade_surface.fill(BLACK)
            fade_surface.set_alpha(fade_alpha)
            SCREEN.blit(fade_surface, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                running = False
        pygame.display.flip()
    SCREEN.fill(BLACK)
    pygame.display.flip()
    pygame.time.delay(300)


def main_menu():
    clock = pygame.time.Clock()
    running = True
    dt = 1 / 60
    start_clicked_time = 0
    exit_clicked_time = 0
    click_animation_duration = 0.3

    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if start_button.handle_click(event) and start_clicked_time == 0:
                print("Start button clicked!")
                start_clicked_time = click_animation_duration
            if exit_button.handle_click(event) and exit_clicked_time == 0:
                print("Exit button clicked!")
                exit_clicked_time = click_animation_duration

        start_button.check_hover(mouse_pos)
        exit_button.check_hover(mouse_pos)
        start_button.update_animation(dt)
        exit_button.update_animation(dt)

        if start_clicked_time > 0:
            start_clicked_time -= dt
            if start_clicked_time <= 0:
                start_clicked_time = 0
                story_screen()
                game_loop()

        if exit_clicked_time > 0:
            exit_clicked_time -= dt
            if exit_clicked_time <= 0:
                exit_clicked_time = 0
                shutdown_animation()
                pygame.quit()
                sys.exit()

        draw_menu()
        pygame.display.flip()
        dt = clock.tick(60) / 1000


# Button dimensions
start_button_width = 256
start_button_height = 87
exit_button_width = 256
exit_button_height = 78

start_animation_path = os.path.join("Images", "StartButtonPNG")
exit_animation_path = os.path.join("Images", "ExitButtonPng")

start_button = PixelButton(
    WIDTH // 2 - start_button_width // 2, HEIGHT // 2 + 50,
    start_button_width, start_button_height, "START",
    "Images\\START_BUTTON.png", start_animation_path
)

exit_button = PixelButton(
    WIDTH // 2 - exit_button_width // 2, HEIGHT // 2 + 150,
    exit_button_width, exit_button_height, "EXIT",
    "Images\\EXIT_BUTTON.png", exit_animation_path
)

back_button = PixelButton(
    WIDTH // 2 - exit_button_width // 2, HEIGHT - 150,
    exit_button_width, exit_button_height, "BACK TO MENU"
)

if __name__ == "__main__":
    main_menu()