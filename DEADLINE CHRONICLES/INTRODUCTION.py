import pygame
import sys
import os

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = pygame.math.Vector2()
        display_surface = pygame.display.get_surface()
        if display_surface is None:
            raise RuntimeError("Pygame display must be initialized before creating CameraGroup")
        self.half_width = display_surface.get_width() // 2
        self.half_height = display_surface.get_height() // 2

        # Set zoom factor to show a bit more of the screen (2.2x2.2 grid)
        self.zoom_factor = 2.2  # Reduced from 2.8 to zoom out a little bit

        # Create a viewport surface for the visible area
        self.viewport_width = int(display_surface.get_width() // 2.2)
        self.viewport_height = int(display_surface.get_height() // 2.2)
        self.viewport = pygame.Surface((self.viewport_width, self.viewport_height))

        # Reference to collision layer for depth sorting
        self.collision_layer = None

    def custom_draw(self, screen, player):
        # Calculate offset based on player position
        # This centers the player in the small viewport
        self.offset.x = player.rect.centerx - self.viewport_width // 2
        self.offset.y = player.rect.centery - self.viewport_height // 2

        # Y-sort sprites by their bottom edge for proper depth rendering
        sprites_list = list(self.sprites())

        # Separate background sprites from other sprites
        background_sprites = [sprite for sprite in sprites_list if isinstance(sprite, Introduction_Background)]
        other_sprites = [sprite for sprite in sprites_list if not isinstance(sprite, Introduction_Background)]

        # Sort other sprites by their bottom Y coordinate (Y-sorting)
        other_sprites.sort(key=lambda sprite: sprite.rect.bottom)

        # Clear the viewport with black
        self.viewport.fill(BLACK)

        # Draw background first
        for sprite in background_sprites:
            offset_rect = sprite.rect.copy()
            offset_rect.topleft = (offset_rect.x - self.offset.x, offset_rect.y - self.offset.y)

            if (offset_rect.right > 0 and offset_rect.bottom > 0 and
                    offset_rect.left < self.viewport_width and offset_rect.top < self.viewport_height):
                self.viewport.blit(sprite.image, offset_rect)

        # Draw other sprites with Y-sorting
        for sprite in other_sprites:
            offset_rect = sprite.rect.copy()
            offset_rect.topleft = (offset_rect.x - self.offset.x, offset_rect.y - self.offset.y)

            if (offset_rect.right > 0 and offset_rect.bottom > 0 and
                    offset_rect.left < self.viewport_width and offset_rect.top < self.viewport_height):
                self.viewport.blit(sprite.image, offset_rect)

        # Scale the viewport up to fill the screen (Undertale-style)
        scaled_viewport = pygame.transform.scale(self.viewport, (screen.get_width(), screen.get_height()))
        screen.blit(scaled_viewport, (0, 0))


class CollisionObject(pygame.sprite.Sprite):
    """Invisible collision object for furniture"""

    def __init__(self, x, y, width, height, name=""):
        super().__init__()
        # Create invisible collision box
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))  # Transparent
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name

    def draw_debug(self, surface, offset):
        """Draw collision box for debugging"""
        debug_rect = self.rect.copy()
        debug_rect.x -= offset.x
        debug_rect.y -= offset.y
        pygame.draw.rect(surface, RED, debug_rect, 2)


class CollisionManager:
    """Manages all collision objects in the scene"""

    def __init__(self, background_sprite):
        self.collision_objects = pygame.sprite.Group()
        self.background_sprite = background_sprite
        self.setup_restaurant_collisions()

    def setup_restaurant_collisions(self):
        """Create collision boxes for restaurant furniture based on the scaled layout"""
        # Get the background dimensions and position
        bg_rect = self.background_sprite.rect
        bg_width = self.background_sprite.width
        bg_height = self.background_sprite.height

        # Calculate the offset from the background's top-left corner
        offset_x = bg_rect.left
        offset_y = bg_rect.top

        # Scale factor based on actual background size vs original coordinates
        # Assuming original coordinates were based on a ~500x900 image
        scale_x = bg_width / 500.0
        scale_y = bg_height / 900.0

        # Helper function to scale and position coordinates
        def scaled_collision(x, y, w, h, name):
            scaled_x = int(x * scale_x) + offset_x
            scaled_y = int(y * scale_y) + offset_y
            scaled_w = int(w * scale_x)
            scaled_h = int(h * scale_y)
            self.add_collision(scaled_x, scaled_y, scaled_w, scaled_h, name)

        # Tables - Main dining area (white rectangular surfaces)
        # Adjusted coordinates based on your screenshot
        # Top table with chairs (the one visible in screenshot)
        scaled_collision(300, 350, 120, 80, "MainTable")

        # Lower table
        scaled_collision(300, 480, 120, 60, "LowerTable")

        # Side boundaries to prevent walking off the brown tiled area
        # Left boundary
        scaled_collision(0, 0, 50, bg_height, "LeftWall")
        # Right boundary
        scaled_collision(bg_width - 50, 0, 50, bg_height, "RightWall")
        # Top boundary
        scaled_collision(0, 0, bg_width, 100, "TopWall")
        # Bottom boundary
        scaled_collision(0, bg_height - 50, bg_width, 50, "BottomWall")

    def add_collision(self, x, y, width, height, name=""):
        """Add a collision object to the manager"""
        collision_obj = CollisionObject(x, y, width, height, name)
        self.collision_objects.add(collision_obj)

    def check_collision(self, rect):
        """Check if a rectangle collides with any collision objects"""
        for collision_obj in self.collision_objects:
            if rect.colliderect(collision_obj.rect):
                return collision_obj
        return None

    def draw_debug(self, surface, offset):
        """Draw all collision boxes for debugging"""
        for collision_obj in self.collision_objects:
            collision_obj.draw_debug(surface, offset)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, collision_manager):
        super().__init__()
        # Load Harold sprite images for different directions
        self.sprites = {
            'back': None,  # HAROLD_1 - facing back (up)
            'right': None,  # HAROLD_2 - facing right
            'left': None,  # HAROLD_3 - facing left
            'front': None  # HAROLD_4 - facing down
        }

        # Load the sprites
        try:
            self.sprites['back'] = pygame.image.load('Images\\SPRITES\\CHARACTER_SPRITES\\HAROLD\\HAROLD_1.png')
            self.sprites['right'] = pygame.image.load('Images\\SPRITES\\CHARACTER_SPRITES\\HAROLD\\HAROLD_2.png')
            self.sprites['left'] = pygame.image.load('Images\\SPRITES\\CHARACTER_SPRITES\\HAROLD\\HAROLD_3.png')
            self.sprites['front'] = pygame.image.load('Images\\SPRITES\\CHARACTER_SPRITES\\HAROLD\\HAROLD_4.png')

            # Scale all sprites to make them more visible (80x80 pixels)
            for direction in self.sprites:
                if self.sprites[direction]:
                    self.sprites[direction] = pygame.transform.scale(self.sprites[direction], (120, 120))
        except pygame.error as e:
            print(f"Warning: Could not load Harold sprites: {e}")
            # Create fallback colored rectangles if image loading fails
            for direction in self.sprites:
                fallback = pygame.Surface((80, 80))
                fallback.fill((255, 0, 0))  # Red color as fallback
                self.sprites[direction] = fallback

        # Set initial direction and image
        self.direction = 'front'  # Start facing front
        self.image = self.sprites[self.direction]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 5

        # Track last movement for direction when not moving
        self.last_movement = None

        # Store collision manager reference
        self.collision_manager = collision_manager

    def update(self, keys):
        # Store original position
        original_x = self.rect.x
        original_y = self.rect.y

        # Track if any movement happened this frame
        moved = False

        # Handle movement based on key presses with collision detection
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            # Try moving up
            self.rect.y -= self.speed
            if self.collision_manager.check_collision(self.rect):
                self.rect.y = original_y  # Revert movement if collision
            else:
                self.direction = 'back'  # HAROLD_1
                moved = True
                self.last_movement = 'back'

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            # Try moving down
            self.rect.y += self.speed
            if self.collision_manager.check_collision(self.rect):
                self.rect.y = original_y  # Revert movement if collision
            else:
                self.direction = 'front'  # HAROLD_4
                moved = True
                self.last_movement = 'front'

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            # Try moving left
            self.rect.x -= self.speed
            if self.collision_manager.check_collision(self.rect):
                self.rect.x = original_x  # Revert movement if collision
            else:
                self.direction = 'left'  # HAROLD_3
                moved = True
                self.last_movement = 'left'

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            # Try moving right
            self.rect.x += self.speed
            if self.collision_manager.check_collision(self.rect):
                self.rect.x = original_x  # Revert movement if collision
            else:
                self.direction = 'right'  # HAROLD_2
                moved = True
                self.last_movement = 'right'

        # If no movement this frame but we have a last movement, keep that direction
        if not moved and self.last_movement:
            self.direction = self.last_movement

        # Update the image based on direction
        self.image = self.sprites[self.direction]


class Introduction_Background(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()  # Call parent constructor with no arguments

        # Store dimensions
        self.width = width
        self.height = height

        # Try to load background image
        try:
            original_image = pygame.image.load('Images\\SPRITES\\MAP.png')
            original_width, original_height = original_image.get_size()
            print(f"Original MAP.png dimensions: {original_width}x{original_height}")

            # Calculate the scale factor needed to ensure the map covers the entire screen
            # while maintaining aspect ratio
            scale_x = width / original_width
            scale_y = height / original_height
            scale_factor = max(scale_x, scale_y)  # Use the larger scale factor to ensure no black bars

            # Scale the image to at least the size of the screen
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            self.image = pygame.transform.scale(original_image, (new_width, new_height))
            self.width, self.height = new_width, new_height
            print(f"Scaled MAP.png to: {new_width}x{new_height} to ensure no black bars")

        except pygame.error:
            print("Warning: Could not load background image 'Images\\SPRITES\\MAP.png'")
            # Create a default background if image loading fails
            self.image = pygame.Surface((width, height))
            self.width, self.height = width, height
            self.image.fill((50, 50, 100))  # Dark blue background

        # Set up the rectangle - position it at the center
        self.rect = self.image.get_rect()
        self.rect.center = (width // 2, height // 2)


def introduction_main():  # Renamed from 'main' to 'introduction_main'
    # Initialize Pygame and create display first
    if not pygame.get_init():
        pygame.init()

    # If no display exists, create one
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((800, 600))  # Default size if not already set

    # Now create the camera group
    camera_group = CameraGroup()

    # Get the screen from the main game
    SCREEN = pygame.display.get_surface()
    WIDTH, HEIGHT = SCREEN.get_size()

    # Fill screen with black initially
    SCREEN.fill(BLACK)
    pygame.display.flip()

    # Create background sprite with proper initialization FIRST
    background = Introduction_Background(WIDTH, HEIGHT)
    camera_group.add(background)

    # Create collision manager with the background sprite
    collision_manager = CollisionManager(background)

    # Create player sprite with collision manager
    player = Player(WIDTH // 2, HEIGHT // 2, collision_manager)
    camera_group.add(player)

    # Add instruction text
    font = pygame.font.SysFont("Arial", 18)
    instruction_text = "WASD/Arrow Keys: Move | ESC: Exit | F1: Toggle Debug"
    text_surface = font.render(instruction_text, True, WHITE)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - 30))

    # Debug mode toggle
    debug_mode = False

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
                elif event.key == pygame.K_F1:
                    debug_mode = not debug_mode
                    print(f"Debug mode: {'ON' if debug_mode else 'OFF'}")

        # Get keyboard state for continuous movement
        keys = pygame.key.get_pressed()

        # Update player based on keyboard input
        player.update(keys)

        # Fill screen with black before drawing sprites
        SCREEN.fill(BLACK)

        # Draw all sprites with camera following player
        camera_group.custom_draw(SCREEN, player)

        # Draw collision boxes in debug mode
        if debug_mode:
            collision_manager.draw_debug(camera_group.viewport, camera_group.offset)
            # Scale and draw the debug viewport
            debug_viewport = pygame.transform.scale(camera_group.viewport, (SCREEN.get_width(), SCREEN.get_height()))
            SCREEN.blit(debug_viewport, (0, 0))

        # Draw instruction text (fixed position, not affected by camera)
        SCREEN.blit(text_surface, text_rect)

        # Update display
        pygame.display.flip()
        clock.tick(60)


# Keep the original main function for standalone execution
def main():
    introduction_main()


if __name__ == "__main__":
    main()