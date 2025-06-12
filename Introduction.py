import pygame

def show_introduction():
    pygame.init()

    # Screen setup
    SCREEN = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Deadline Chronicles")
    clock = pygame.time.Clock()

    # Load Harold sprites
    try:
        harold_up = pygame.image.load("Images\\SPRITES\\CHARACTER_SPRITES\\HAROLD\\HAROLD_1.png")
        harold_right = pygame.image.load("Images\\SPRITES\\CHARACTER_SPRITES\\HAROLD\\HAROLD_2.png")
        harold_left = pygame.image.load("Images\\SPRITES\\CHARACTER_SPRITES\\HAROLD\\HAROLD_3.png")
        harold_down = pygame.image.load("Images\\SPRITES\\CHARACTER_SPRITES\\HAROLD\\HAROLD_4.png")
    except pygame.error as e:
        print(f"Error loading images: {e}")
        pygame.quit()
        return

    # Scale sprites if needed (adjust size)
    HAROLD_SIZE = (100, 100)  # Set desired size
    harold_up = pygame.transform.scale(harold_up, HAROLD_SIZE)
    harold_right = pygame.transform.scale(harold_right, HAROLD_SIZE)
    harold_left = pygame.transform.scale(harold_left, HAROLD_SIZE)
    harold_down = pygame.transform.scale(harold_down, HAROLD_SIZE)

    # Initial settings
    x, y = 600, 300  # Starting position
    speed = 5
    current_sprite = harold_down  # Default facing direction

    running = True
    while running:
        dt = clock.tick(60) / 1000  # Delta time in seconds
        SCREEN.fill((0, 0, 0))  # Clear screen

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Exit on ESC key
        if keys[pygame.K_ESCAPE]:
            running = False

        dx, dy = 0, 0

        # Only update direction/sprite if movement key is pressed
        if keys[pygame.K_w]:  # UP
            dy = -speed
            current_sprite = harold_up
        elif keys[pygame.K_s]:  # DOWN
            dy = speed
            current_sprite = harold_down
        elif keys[pygame.K_a]:  # LEFT
            dx = -speed
            current_sprite = harold_left
        elif keys[pygame.K_d]:  # RIGHT
            dx = speed
            current_sprite = harold_right

        # Update position
        x += dx
        y += dy

        # Keep Harold inside the screen bounds
        x = max(0, min(x, 1280 - HAROLD_SIZE[0]))
        y = max(0, min(y, 720 - HAROLD_SIZE[1]))

        # Draw Harold
        SCREEN.blit(current_sprite, (x, y))

        # Update display
        pygame.display.flip()

    pygame.quit()

# Call the function to show the introduction
show_introduction()