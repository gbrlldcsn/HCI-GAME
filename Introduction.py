import pygame
import os

class Camera:
    def __init__(self, width, height, map_width, map_height):
        self.width = width
        self.height = height
        self.zoom = 4  # Zoom level to show 1/4th of the map
        # Center the camera on the middle of the map
        self.center_x = map_width // 2
        self.center_y = map_height // 2
        self.offset_x = -30  # Nudge left for better centering (adjust as needed)
        self.offset_y = -310  # Start lower for whiteboard area (adjust as needed)
        self.map_width = map_width
        self.map_height = map_height
        # Calculate panning limits
        self.max_offset = (self.map_height // 2) - (self.height // (2 * self.zoom))
        self.min_offset = -self.max_offset

    def auto_pan_down(self, speed=1):
        # Slowly pan down, stop at the bottom
        if self.offset_y < self.max_offset:
            self.offset_y += speed
            if self.offset_y > self.max_offset:
                self.offset_y = self.max_offset

    def reset_offset(self):
        self.offset_y = -310  # Reset to initial starting position

    def apply(self, image):
        # Calculate the scaled size of the image
        scaled_width = image.get_width() * self.zoom
        scaled_height = image.get_height() * self.zoom
        scaled_image = pygame.transform.scale(image, (scaled_width, scaled_height))

        # Calculate the top-left corner of the camera view in the original image
        view_x = self.center_x - (self.width // (2 * self.zoom)) + self.offset_x
        view_y = self.center_y - (self.height // (2 * self.zoom)) + self.offset_y

        # Crop the correct portion from the original image before scaling
        crop_rect = pygame.Rect(view_x, view_y, self.width // self.zoom, self.height // self.zoom)
        cropped_image = image.subsurface(crop_rect)
        zoomed_image = pygame.transform.scale(cropped_image, (self.width, self.height))
        return zoomed_image, view_x, view_y

def pan_map_without_npc(SCREEN, clock, camera, map_image):
    running = True
    pan_finished = False
    while running:
        dt = clock.tick(60) / 1000
        SCREEN.fill((0, 0, 0))

        # Auto pan down
        if camera.offset_y < camera.max_offset:
            camera.auto_pan_down(speed=1)  # Adjust speed as needed
        else:
            pan_finished = True

        # Draw the zoomed and cropped map
        zoomed_map, view_x, view_y = camera.apply(map_image)
        SCREEN.blit(zoomed_map, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

        pygame.display.flip()

        # If panning is finished, break
        if pan_finished:
            break

def pan_map_with_npc(SCREEN, clock, camera, map_image, npc_image, npc_pos_on_map):
    running = True
    pan_finished = False
    while running:
        dt = clock.tick(60) / 1000
        SCREEN.fill((0, 0, 0))

        # Auto pan down
        if camera.offset_y < camera.max_offset:
            camera.auto_pan_down(speed=1)  # Adjust speed as needed
        else:
            pan_finished = True

        # Draw the zoomed and cropped map
        zoomed_map, view_x, view_y = camera.apply(map_image)
        SCREEN.blit(zoomed_map, (0, 0))

        # Calculate NPC position relative to the camera view
        npc_x_on_screen = (npc_pos_on_map[0] - view_x) * camera.zoom
        npc_y_on_screen = (npc_pos_on_map[1] - view_y) * camera.zoom
        SCREEN.blit(npc_image, (npc_x_on_screen, npc_y_on_screen))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

        pygame.display.flip()

        # If panning is finished, break
        if pan_finished:
            break

def show_introduction(SCREEN=None, clock=None):
    if not pygame.get_init():
        pygame.init()
    if SCREEN is None:
        SCREEN_WIDTH = 1280
        SCREEN_HEIGHT = 720
        SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Deadline Chronicles")
    else:
        SCREEN_WIDTH = SCREEN.get_width()
        SCREEN_HEIGHT = SCREEN.get_height()
    if clock is None:
        clock = pygame.time.Clock()

    # Load the map background
    try:
        map_path = os.path.join("Images", "SPRITES", "MAP.png")
        map_image = pygame.image.load(map_path)
    except pygame.error as e:
        print(f"Error loading map image: {e}")
        return

    # Load the NPC sprite
    try:
        npc_path = os.path.join("Images", "SPRITES", "CHARACTER_SPRITES", "2nd NpcSprite", "npc2_front.png")
        npc_image = pygame.image.load(npc_path)
        npc_image = pygame.transform.scale(npc_image, (200, 200))  # Adjust size as needed
    except pygame.error as e:
        print(f"Error loading NPC image: {e}")
        return

    # Position of the NPC on the map (adjust as needed)
    npc_pos_on_map = ((map_image.get_width() // 2) - 50, 220)  # Centered horizontally with left offset, positioned at whiteboard area

    # Initialize camera with map size
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, map_image.get_width(), map_image.get_height())

    # First pan (map only)
    pan_map_without_npc(SCREEN, clock, camera, map_image)

    # Show black screen for 1 second as a transition
    SCREEN.fill((0, 0, 0))
    pygame.display.flip()
    pygame.time.delay(1000)  # 1000 ms = 1 second

    # Reset camera and pan again (with NPC)
    camera.reset_offset()
    pan_map_with_npc(SCREEN, clock, camera, map_image, npc_image, npc_pos_on_map)

    if SCREEN is None:
        pygame.quit()
    return

if __name__ == "__main__":
    show_introduction()
