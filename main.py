# zombie car that shoots
# zombies spawn in
import pygame
import os
import random
pygame.font.init()

WIDTH, HEIGHT = 900, 700
LEFT_BORDER, RIGHT_BORDER = 150, 790
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Survival")

GREEN = (0, 255, 0)
RED = (255, 0, 0)

# load images
CAR_IMAGE = pygame.image.load(os.path.join("zombie_game", "race_car.png"))
CAR = pygame.transform.scale(CAR_IMAGE, (90, 150))

BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("zombie_game", "highway.png")), (WIDTH, HEIGHT))

GUN_IMAGE = pygame.image.load(os.path.join("zombie_game", "real_bullet.png"))
GUN_SIZE = pygame.transform.scale(GUN_IMAGE, (50, 50))
GUN_SHOT = pygame.transform.rotate(GUN_SIZE, 90)
# bullet for the soldier
SOLDIER_SHOT = pygame.transform.rotate(GUN_SIZE, 270)

ZOMBIE_IMAGE = pygame.image.load(os.path.join("zombie_game", "zombie.png"))
ZOMBIE_SIZE = pygame.transform.scale(ZOMBIE_IMAGE, (70, 70))
ZOMBIE = pygame.transform.rotate(ZOMBIE_SIZE, 270)

SHOOTER_IMAGE = pygame.image.load(os.path.join("zombie_game", "lone_survivor.png"))
SHOOTER_SIZE = pygame.transform.scale(SHOOTER_IMAGE, (50, 50))
SHOOTER = pygame.transform.rotate(SHOOTER_SIZE, 270)  # Rotate


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Car:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.car_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.car_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):  # remove laser once off the screen
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10  # health loss for our player
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.car_img.get_width()

    def get_height(self):
        return self.car_img.get_height()


class Player(Car):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.car_img = CAR
        self.laser_img = GUN_SHOT
        # mask for pixel collision
        self.mask = pygame.mask.from_surface(self.car_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):  # remove laser once off the screen
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, RED, (self.x, self.y + self.car_img.get_height() + 10, self.car_img.get_width(), 10))
        pygame.draw.rect(window, GREEN, (self.x, self.y + self.car_img.get_height() + 10,
                                             self.car_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Car):
    COLOR_MAP = {
        "shooter": (SHOOTER, SOLDIER_SHOT),
        "zombie": (ZOMBIE, SOLDIER_SHOT)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.car_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.car_img)

    # move the enemies
    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 60
    level = 1
    lives = 4
    main_font = pygame.font.SysFont("Verdana", 20)
    lost_font = pygame.font.SysFont("Verdana", 50)

    enemies = []
    wave_length = 3
    enemy_velocity = 2

    car_velocity = 5  # move 5 pixels
    laser_velocity = 6

    player = Player(450, 500)  # player spawn
    clock = pygame.time.Clock()  # make games control
    lost = False
    lost_count = 0

    def draw_window():
        WIN.blit(BACKGROUND, (0, 0))
        lives_label = main_font.render(f"Lives: {lives}", 1, GREEN)
        level_label = main_font.render(f"Level: {level}", 1, GREEN)

        WIN.blit(lives_label, (50, 40))  # Positions of lives,level
        WIN.blit(level_label, (50, 80))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("YOU Lost :(", 1, RED)
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        draw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 4
            for i in range(wave_length):   # zombies position spawn
                enemy = Enemy(random.randrange(150, 700), random.randrange(-1500, -100),
                              random.choice(["shooter", "zombie"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # would quit when X on right corner
                run = False
        # track keys being press
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - car_velocity > LEFT_BORDER:  # left
            player.x -= car_velocity
        if keys[pygame.K_d] and player.x + car_velocity + player.get_width() < RIGHT_BORDER:  # right
            player.x += car_velocity
        if keys[pygame.K_w] and player.y - car_velocity > 0:  # up
            player.y -= car_velocity
        if keys[pygame.K_s] and player.y + car_velocity + player.get_height() + 15 < HEIGHT:  # down
            player.y += car_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)

            if random.randrange(0, 2*60) == 1:  # probability enemy shoot
                enemy.shoot()

            if collide(enemy, player): # collision with player
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_velocity, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        WIN.blit(BACKGROUND, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, GREEN)
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
