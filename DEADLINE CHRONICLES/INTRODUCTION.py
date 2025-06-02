import pygame
import sys
import os

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def main():
    # Get the screen from the main game
    SCREEN = pygame.display.get_surface()
    WIDTH, HEIGHT = SCREEN.get_size()

    # Clear the entire screen to ensure no text from story_screen remains
    SCREEN.fill(BLACK)
    # Update the display immediately to ensure the screen is cleared
    pygame.display.flip()

    # Load menu background image
    try:
        menu_bg_img = pygame.image.load('Images\\SPRITES\\MAP.png')
        # Using original dimensions of the image without scaling
        bg_width, bg_height = menu_bg_img.get_size()
        print(f"Background image dimensions: {bg_width}x{bg_height}")
    except pygame.error:
        print("Warning: Could not load background image 'Images\\SPRITES\\MAP.png'")
        menu_bg_img = None

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

        # Fill screen with background
        if menu_bg_img is not None:
            # Calculate position to center the image
            img_width, img_height = menu_bg_img.get_size()
            x = (WIDTH - img_width) // 2
            y = (HEIGHT - img_height) // 2
            SCREEN.blit(menu_bg_img, (x, y))

            # Draw collision layer on top of the background, scaled to match the MAP.png
            if collision_layer_img is not None:
                # Get the dimensions of the background image
                bg_width, bg_height = menu_bg_img.get_size()

                # Scale the collision layer to match the background image dimensions
                scaled_collision_layer = pygame.transform.scale(collision_layer_img, (bg_width, bg_height))

                # Position the scaled collision layer at the same position as the background
                SCREEN.blit(scaled_collision_layer, (x, y))
        else:
            # Fallback to black background if image isn't available
            SCREEN.fill(BLACK)

        # Add instruction text to let the user know how to continue
        # Try to use the pixel fonts from Main Game.py if available

        # Update display
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
