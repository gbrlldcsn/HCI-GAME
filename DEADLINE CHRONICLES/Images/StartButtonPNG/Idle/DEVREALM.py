import pygame
import random
import string
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1280, 720
FPS = 60
FONT_SIZE = 20
COLUMNS = WIDTH // FONT_SIZE

# Colors
BLACK = (0, 0, 0)
RED = (209, 51, 55)  # #D13337
BLUE = (81, 163, 184)  # #51A3B8
COLORS = [BLUE, RED]
SHAPE_COLORS = [(RED[0], RED[1], RED[2], 30), (BLUE[0], BLUE[1], BLUE[2], 30)]  # Semi-transparent

# Characters for the matrix effect
MATRIX_CHARS = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"


class RotatingShape:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.size = random.randint(20, 100)
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)
        self.shape_type = random.choice(['triangle', 'square', 'pentagon', 'hexagon'])
        self.color = random.choice(SHAPE_COLORS)
        self.drift_x = random.uniform(-0.5, 0.5)
        self.drift_y = random.uniform(-0.5, 0.5)

    def update(self):
        self.rotation += self.rotation_speed
        self.x += self.drift_x
        self.y += self.drift_y

        # Wrap around screen
        if self.x < -self.size:
            self.x = WIDTH + self.size
        elif self.x > WIDTH + self.size:
            self.x = -self.size
        if self.y < -self.size:
            self.y = HEIGHT + self.size
        elif self.y > HEIGHT + self.size:
            self.y = -self.size

    def draw(self, screen):
        # Create a surface for the shape with alpha
        shape_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)

        # Calculate points for different shapes
        points = []
        if self.shape_type == 'triangle':
            num_points = 3
        elif self.shape_type == 'square':
            num_points = 4
        elif self.shape_type == 'pentagon':
            num_points = 5
        else:  # hexagon
            num_points = 6

        for i in range(num_points):
            angle = (2 * math.pi * i / num_points) + math.radians(self.rotation)
            x = self.size + self.size * 0.8 * math.cos(angle)
            y = self.size + self.size * 0.8 * math.sin(angle)
            points.append((x, y))

        # Draw the shape
        pygame.draw.polygon(shape_surf, self.color, points)
        pygame.draw.polygon(shape_surf, (*self.color[:3], min(100, self.color[3] * 2)), points, 2)

        # Blit to main screen
        screen.blit(shape_surf, (self.x - self.size, self.y - self.size))


class MatrixDrop:
    def __init__(self, x):
        self.x = x
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.uniform(2, 8)
        self.char = random.choice(MATRIX_CHARS)
        self.color = random.choice(COLORS)
        self.trail_length = random.randint(8, 20)

    def update(self):
        self.y += self.speed
        # Change character every frame
        self.char = random.choice(MATRIX_CHARS)

        # Reset when off screen
        if self.y > HEIGHT + FONT_SIZE:
            self.y = random.randint(-HEIGHT, -FONT_SIZE)
            self.speed = random.uniform(2, 8)
            self.color = random.choice(COLORS)
            self.trail_length = random.randint(8, 20)

    def draw(self, screen, font):
        # Draw the trail
        for i in range(self.trail_length):
            trail_y = self.y - (i * FONT_SIZE)
            if trail_y > -FONT_SIZE and trail_y < HEIGHT:
                # Fade the trail
                alpha = max(0, 255 - (i * 15))
                trail_color = (*self.color, alpha)

                # Create surface for alpha blending
                trail_surf = pygame.Surface((FONT_SIZE, FONT_SIZE), pygame.SRCALPHA)
                trail_char = random.choice(MATRIX_CHARS)  # Different char for each trail segment
                char_surf = font.render(trail_char, True, (*self.color, alpha))
                trail_surf.blit(char_surf, (0, 0))

                # Adjust alpha for fading effect
                fade_factor = alpha / 255.0
                faded_color = (
                    int(self.color[0] * fade_factor),
                    int(self.color[1] * fade_factor),
                    int(self.color[2] * fade_factor)
                )

                char_surf = font.render(trail_char, True, faded_color)
                screen.blit(char_surf, (self.x, trail_y))


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Matrix Rain with Rotating Shapes")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, FONT_SIZE)

    # Create drops for each column
    drops = []
    for i in range(COLUMNS):
        x = i * FONT_SIZE
        # Create multiple drops per column with different starting positions
        for j in range(random.randint(1, 3)):
            drop = MatrixDrop(x)
            drop.y = random.randint(-HEIGHT * 2, HEIGHT)
            drops.append(drop)

    # Create rotating shapes
    shapes = []
    for _ in range(random.randint(5, 12)):
        shapes.append(RotatingShape())

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Fill screen with black
        screen.fill(BLACK)

        # Update and draw rotating shapes (behind matrix)
        for shape in shapes:
            shape.update()
            shape.draw(screen)

        # Update and draw all drops (in front of shapes)
        for drop in drops:
            drop.update()
            drop.draw(screen, font)

        # Randomly add new drops
        if random.random() < 0.02:  # 2% chance each frame
            x = random.randint(0, COLUMNS - 1) * FONT_SIZE
            new_drop = MatrixDrop(x)
            new_drop.y = random.randint(-HEIGHT, -FONT_SIZE)
            drops.append(new_drop)

        # Remove drops that are way off screen (cleanup)
        drops = [drop for drop in drops if drop.y < HEIGHT + FONT_SIZE * 2]

        # Occasionally add or remove shapes
        if random.random() < 0.001:  # Very rare chance to add shape
            if len(shapes) < 15:
                shapes.append(RotatingShape())
        elif random.random() < 0.0005 and len(shapes) > 3:  # Rare chance to remove shape
            shapes.pop(random.randint(0, len(shapes) - 1))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()