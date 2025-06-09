import pygame
import sys

# === Colors === #
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)


# === Utility Classes === #
# The CollisionObject and CollisionManager classes are removed.


# === Visual Classes === #
class Introduction_Background(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height
        try:
            img = pygame.image.load('Images/SPRITES/MAP.png')
            ow, oh = img.get_size()
            scale = max(width / ow, height / oh)
            nw, nh = int(ow * scale), int(oh * scale)
            self.image = pygame.transform.scale(img, (nw, nh))
            self.width, self.height = nw, nh
        except:
            self.image = pygame.Surface((width, height))
            self.image.fill((50, 50, 100))
        self.rect = self.image.get_rect(center=(width // 2, height // 2))


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y): # collision_manager parameter removed
        super().__init__()
        self.sprites = {}
        try:
            for d, i in zip(['back', 'right', 'left', 'front'], range(1, 5)):
                img = pygame.image.load(f'Images/SPRITES/CHARACTER_SPRITES/HAROLD/HAROLD_{i}.png')
                self.sprites[d] = pygame.transform.scale(img, (110, 110))
        except:
            for d in ['back', 'right', 'left', 'front']:
                surface = pygame.Surface((80, 80))
                surface.fill(RED)
                self.sprites[d] = surface

        self.direction = 'front'
        self.image = self.sprites[self.direction]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.last_movement = None
        # self.collision_manager = collision_manager # removed

    def update(self, keys):
        dx = dy = 0
        # orig_x, orig_y = self.rect.x, self.rect.y # no longer needed
        moved = False

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.speed; self.direction = 'back'; moved = True
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.speed; self.direction = 'front'; moved = True
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed; self.direction = 'left'; moved = True
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed; self.direction = 'right'; moved = True

        self.rect.x += dx
        self.rect.y += dy
        # The collision check and rollback are removed:
        # if self.collision_manager.check_collision(self.rect):
        #     self.rect.x, self.rect.y = orig_x, orig_y

        if moved:
            self.last_movement = self.direction
        elif self.last_movement:
            self.direction = self.last_movement
        self.image = self.sprites[self.direction]


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = pygame.math.Vector2()
        screen = pygame.display.get_surface()
        self.vw = screen.get_width() // 2.2
        self.vh = screen.get_height() // 2.2
        self.viewport = pygame.Surface((self.vw, self.vh))

    def custom_draw(self, screen, player):
        self.offset.x = player.rect.centerx - self.vw // 2
        self.offset.y = player.rect.centery - self.vh // 2
        self.viewport.fill(BLACK)

        # Draw background first
        for sprite in self.sprites():
            if isinstance(sprite, Introduction_Background):
                offset_rect = sprite.rect.copy()
                offset_rect.topleft -= self.offset
                if 0 < offset_rect.right and offset_rect.left < self.vw and 0 < offset_rect.bottom and offset_rect.top < self.vh:
                    self.viewport.blit(sprite.image, offset_rect)
                break # Assuming there's only one background

        # Draw other sprites, sorted by bottom for correct layering
        for sprite in sorted(self.sprites(), key=lambda s: getattr(s, 'rect', pygame.Rect(0, 0, 0, 0)).bottom):
            if not hasattr(sprite, 'rect') or isinstance(sprite, Introduction_Background):
                continue
            offset_rect = sprite.rect.copy()
            offset_rect.topleft -= self.offset
            if 0 < offset_rect.right and offset_rect.left < self.vw and 0 < offset_rect.bottom and offset_rect.top < self.vh:
                self.viewport.blit(sprite.image, offset_rect)

        screen.blit(pygame.transform.scale(self.viewport, screen.get_size()), (0, 0))

# === Main Loop === #
def introduction_main():
    pygame.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((800, 600))
    screen = pygame.display.get_surface()
    width, height = screen.get_size()

    cam_group = CameraGroup()
    bg = Introduction_Background(width, height)
    cam_group.add(bg)

    # collision_manager = CollisionManager(bg) # removed
    player = Player(width // 2, height // 2) # collision_manager argument removed
    cam_group.add(player)

    font = pygame.font.SysFont("Arial", 18)
    instruction_text = font.render("WASD/Arrow Keys: Move | ESC: Exit", True, WHITE) # F1 debug instruction removed
    text_rect = instruction_text.get_rect(center=(width // 2, height - 30))

    # debug = False # removed
    clock = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return
                # elif e.key == pygame.K_F1: # removed
                #     debug = not debug

        keys = pygame.key.get_pressed()
        player.update(keys)
        screen.fill(BLACK)
        cam_group.custom_draw(screen, player)
        # if debug: # removed
        #     collision_manager.draw_debug(cam_group.viewport, cam_group.offset)
        screen.blit(instruction_text, text_rect)
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    introduction_main()