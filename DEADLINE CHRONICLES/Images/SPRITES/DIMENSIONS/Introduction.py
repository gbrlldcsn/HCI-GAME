import pygame
import os

# --- Game Initialization ---
pygame.init() # Initialize all the Pygame modules

# Set up the screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("DEADLINE CHRONICLES") # Set the window title

# --- Sprite Loading Function ---
def load_character_sprites(sprite_folder):
    """
    Loads all PNG sprites from a specified folder into a dictionary.

    Args:
        sprite_folder (str): The path to the folder containing the character sprites.

    Returns:
        dict: A dictionary where keys are sprite filenames (without extension)
              and values are pygame.Surface objects (the loaded sprites).
    """
    character_sprites = {} # Initialize an empty dictionary to store sprites
    try:
        # Check if the sprite folder exists
        if not os.path.exists(sprite_folder):
            print(f"Error: Sprite folder not found at {sprite_folder}")
            return character_sprites # Return empty dictionary if folder doesn't exist

        # Iterate through all files in the specified folder
        for filename in os.listdir(sprite_folder):
            # Check if the file is a PNG image
            if filename.endswith('.png'):
                sprite_path = os.path.join(sprite_folder, filename) # Construct the full path
                try:
                    sprite = pygame.image.load(sprite_path).convert_alpha() # Load the sprite and optimize it with alpha
                    # Store in dictionary with filename as key (without .png extension)
                    character_sprites[filename[:-4]] = sprite
                except pygame.error as e:
                    print(f"Could not load sprite {filename}: {e}")
    except OSError as e:
        print(f"OS error while accessing sprite folder: {e}")

    return character_sprites

# --- Game Variables and Assets ---
# Path to the character sprites folder (relative to where Main_Game.py is run)
SPRITE_BASE_FOLDER = "DEADLINE CHRONICLES/Images/SPRITES/CHARACTER_SPRITES"
HAROLD_SPRITE_FOLDER = os.path.join(SPRITE_BASE_FOLDER, "HAROLD")

# Load Harold's sprites
harold_sprites = load_character_sprites(HAROLD_SPRITE_FOLDER)

# Check if sprites were loaded successfully
if not harold_sprites:
    print("No Harold sprites were loaded. Please check the folder path and contents.")
    # Exit or handle error appropriately if sprites are critical
    pygame.quit()
    exit()

# Get the first sprite to display as an example
# You can change 'HAROLD_1' to 'HAROLD_2', 'HAROLD_3', 'HAROLD_4'
# or implement animation logic here.
current_harold_sprite = harold_sprites.get('HAROLD_1')

# Ensure the sprite exists before trying to get its rect
if current_harold_sprite:
    harold_rect = current_harold_sprite.get_rect()
    # Position Harold in the center bottom of the screen
    harold_rect.centerx = SCREEN_WIDTH // 2
    harold_rect.bottom = SCREEN_HEIGHT - 50 # A little offset from the bottom
else:
    # Fallback if HAROLD_1 is not found
    print("Error: 'HAROLD_1' sprite not found in loaded sprites.")
    harold_rect = pygame.Rect(0, 0, 100, 100) # Placeholder rect

clock = pygame.time.Clock() # To control the game's frame rate
FPS = 60 # Frames per second

# --- Game Loop ---
running = True
while running:
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False # Set running to False to exit the loop

    # Game Logic Updates (e.g., character movement, animation frame changes)
    # For now, we'll keep Harold static.
    # To animate, you'd change `current_harold_sprite` based on time or actions.

    # Drawing (Render / Display)
    screen.fill((0, 0, 0)) # Fill the screen with black each frame to clear previous drawings

    # Draw Harold if the sprite was loaded
    if current_harold_sprite:
        screen.blit(current_harold_sprite, harold_rect)

    pygame.display.flip() # Update the full display Surface to the screen

    # Frame Rate Control
    clock.tick(FPS) # Limit the frame rate to FPS

# --- Quit Pygame ---
pygame.quit() # Uninitialize pygame modules
print("Game exited successfully.")
