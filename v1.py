import pygame, math, random
pygame.init()
pygame.mixer.init()
# setap
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()


kaboom_sound = pygame.mixer.Sound("vine-boom.wav")
kaboom_sound.set_volume(1.0)  # full volume
pixel_width, pixel_height = 160, 120
small_surface = pygame.Surface((pixel_width, pixel_height))


square_size = 16
player = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
pygame.draw.rect(player, (255, 255, 255), (0, 0, square_size, square_size))

x, y = pixel_width // 2, pixel_height // 2
angle = 0
vx, vy = 0, 0
accel = 0.1
friction = 0.98
max_speed = 2.5


bullets = []
enemies = []
boss = None
boss_health = 0
boss_max_health = 0
wave = 1
flash_timer = 0

# sdaijioasdjaijdoaicmamamoamcocmaocmaocmaocoacmaocmaocmaocsmcoakmcapsdicnapcjmadcimopadcosijdcaisojidjcsaiaojdpcsjiadscpijdsacpdiojcasioadscjoidcsjijsdaciojdacsiojpadcijadscpoijadscijoadcspoijdascipojadcsijoasdicojpjiaosd
def spawn_enemy():
    ex = random.randint(10, pixel_width - 10)
    ey = random.randint(10, pixel_height - 10)
    vx = random.choice([-1, 1]) * random.uniform(0.2, 0.6)
    vy = random.choice([-1, 1]) * random.uniform(0.2, 0.6)
    rot_speed = random.uniform(-3, 3)
    return [ex, ey, vx, vy, 0, rot_speed]

def spawn_wave(count):
    for _ in range(count):
        enemies.append(spawn_enemy())

def spawn_boss():
    global boss, boss_health, boss_max_health
    bx = random.randint(20, pixel_width - 20)
    by = random.randint(20, pixel_height - 20)
    boss = [bx, by, 0.4, 0.3, 0]  # posisi
    boss_health = boss_max_health = 20

spawn_wave(4)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:

            bullet_speed = 4
            rad = math.radians(angle)
            bx = x + math.cos(rad) * 10
            by = y - math.sin(rad) * 10
            vx_b = math.cos(rad) * bullet_speed + vx
            vy_b = -math.sin(rad) * bullet_speed + vy
            bullets.append([bx, by, vx_b, vy_b])


    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        angle += 3
    if keys[pygame.K_e]:
        angle -= 3
    rad = math.radians(angle)
    if keys[pygame.K_w]:
        vx += math.cos(rad) * accel
        vy -= math.sin(rad) * accel
    if keys[pygame.K_s]:
        vx -= math.cos(rad) * accel
        vy += math.sin(rad) * accel

    vx *= friction
    vy *= friction


    speed_mag = math.hypot(vx, vy)
    if speed_mag > max_speed:
        vx = vx / speed_mag * max_speed
        vy = vy / speed_mag * max_speed

    x += vx
    y += vy
    x = max(0, min(pixel_width, x))
    y = max(0, min(pixel_height, y))


    if flash_timer > 0:
        small_surface.fill((100, 40, 40))
        flash_timer -= 1
    else:
        small_surface.fill((20, 30, 50))


    rotated = pygame.transform.rotozoom(player, angle, 1)
    rect = rotated.get_rect(center=(x, y))
    small_surface.blit(rotated, rect)


    for enemy in enemies[:]:
        enemy[0] += enemy[2]
        enemy[1] += enemy[3]
        enemy[4] += enemy[5]
        if enemy[0] < 5 or enemy[0] > pixel_width - 5:
            enemy[2] *= -1
        if enemy[1] < 5 or enemy[1] > pixel_height - 5:
            enemy[3] *= -1

        base_enemy = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.rect(base_enemy, (255, 0, 0), (0, 0, 10, 10), width=1)
        rotated_enemy = pygame.transform.rotozoom(base_enemy, enemy[4], 1)
        rect = rotated_enemy.get_rect(center=(enemy[0], enemy[1]))
        small_surface.blit(rotated_enemy, rect)


    if boss:
        boss[0] += boss[2]
        boss[1] += boss[3]
        boss[4] += 1
        if boss[0] < 15 or boss[0] > pixel_width - 15:
            boss[2] *= -1
        if boss[1] < 15 or boss[1] > pixel_height - 15:
            boss[3] *= -1

        base_boss = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(base_boss, (255, 60, 60), (0, 0, 30, 30), width=2)
        rotated_boss = pygame.transform.rotozoom(base_boss, boss[4], 1)
        rect = rotated_boss.get_rect(center=(boss[0], boss[1]))
        small_surface.blit(rotated_boss, rect)


        pygame.draw.rect(small_surface, (20, 30, 50), (30, 5, 100, 5))
        pygame.draw.rect(small_surface, (142, 168, 195),
                         (30, 5, 100 * (boss_health / boss_max_health), 5))
    for bullet in bullets[:]:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]

        if (bullet[0] < 0 or bullet[0] > pixel_width or
            bullet[1] < 0 or bullet[1] > pixel_height):
            bullets.remove(bullet)
            continue
        if boss and abs(bullet[0] - boss[0]) < 18 and abs(bullet[1] - boss[1]) < 18:
            boss_health -= 1
            bullets.remove(bullet)
            flash_timer = 2
            if boss_health <= 0:
                boss = None
                wave += 1
                spawn_wave(wave + 1)
            continue
        for enemy in enemies[:]:
            if abs(bullet[0] - enemy[0]) < 6 and abs(bullet[1] - enemy[1]) < 6:
                kaboom_sound.play()
                enemies.remove(enemy)
                bullets.remove(bullet)
                flash_timer = 2
                break

        pygame.draw.rect(small_surface, (255, 255, 255),
                         (bullet[0], bullet[1], 3, 3))


    if not enemies and boss is None:
        if wave % 5 == 0:
            spawn_boss()
        else:
            wave += 1
            spawn_wave(wave + 1)
    font = pygame.font.Font("Tiny5-Regular.ttf", 20)
    wave_text = font.render(f"Wave {wave}", True, (255, 255, 255))
    small_surface.blit(wave_text, (2, 2))
    pixelated = pygame.transform.scale(small_surface, screen.get_size())
    screen.blit(pixelated, (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
