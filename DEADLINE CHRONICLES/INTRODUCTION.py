import pygame
import sys
import os

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Introduction_Background:
    def __init__(self, screen_width, screen_height):
        try:
            self.image = pygame.image.load('Images\\SPRITES\\MAP.png')
            self.width, self.height = self.image.get_size()
        except pygame.error:
            print("Warning: Could not load background image 'Images\\SPRITES\\MAP.png'")
            self.image = None
            self.width, self.height = 0, 0

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        self.original_y = self.y

        # Panning parameters
        self.pan_speed = 0.5  # Speed of the panning effect
        self.pan_direction = 1  # 1 for down, -1 for up
        self.max_pan = 20  # Maximum distance to pan down
        self.min_pan = -10  # Maximum distance to pan up

    def update(self):
        # Update the y position based on pan direction and speed
        self.y = self.original_y + (self.pan_speed * self.pan_direction)

        # Change direction when reaching the limits
        if self.y >= self.original_y + self.max_pan:
            self.pan_direction = -1
        elif self.y <= self.original_y + self.min_pan:
            self.pan_direction = 1

    def draw(self, screen):
        if self.image is not None:
            screen.blit(self.image, (self.x, self.y))

def main():
    # Get the screen from the main game
    SCREEN = pygame.display.get_surface()
    WIDTH, HEIGHT = SCREEN.get_size()

    # Clear the entire screen to ensure no text from story_screen remains
    SCREEN.fill(BLACK)
    # Update the display immediately to ensure the screen is cleared
    pygame.display.flip()

    # Create background object
    background = Introduction_Background(WIDTH, HEIGHT)

    # Load collision layer image
    try:
        collision_layer_img = pygame.image.load('Images\\SPRITES\\COLLISION_LAYER.png')
        # Get original dimensions of the collision layer
        collision_width, collision_height = collision_layer_img.get_size()
        print(f"Original collision layer dimensions: {collision_width}x{collision_height}")
    except pygame.error:
        print("Warning: Could not load collision layer image 'Images\\SPRITES\\COLLISION_LAYER.png'")
        collision_layer_img = None

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Update and draw background
        background.update()
        background.draw(SCREEN)

        # Draw collision layer on top of the background
        if collision_layer_img is not None and background.image is not None:
            # Get the dimensions of the background image
            bg_width, bg_height = background.width, background.height

            # Scale the collision layer to match the background image dimensions
            scaled_collision_layer = pygame.transform.scale(collision_layer_img, (bg_width, bg_height))

            # Position the scaled collision layer at the same position as the background
            SCREEN.blit(scaled_collision_layer, (background.x, background.y))
        elif background.image is None:
            # Fallback to black background if image isn't available
            SCREEN.fill(BLACK)

        # Add instruction text to let the user know how to continue
        # Try to use the pixel fonts from Main Game.py if available

        # Update display
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
