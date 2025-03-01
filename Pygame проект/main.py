import os
import sys
import random
import math

import pygame
import sqlite3

pygame.init()
screen_info = pygame.display.Info()
pygame.display.set_caption("IMperfect World")
conn2 = sqlite3.connect('Data/Settings.db')
cur2 = conn2.cursor()
size = width, height = 1366, 768
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
hit_enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()
conn1 = sqlite3.connect('Data/data-iw.db')
cur = conn1.cursor()
arial_100 = pygame.font.SysFont('arial', 100)
nav = ''
score = 100
m1_cooldown = 5
active = False
activeG = False
game = False
player_walking = False
play = True
enemy_walking = False


def load_image(name, colorkey=None):
    fullname = os.path.join('Images', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((1, 1))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


player_image = load_image('Hero/Rogue/Idle/Idle-Sheet.png', -1)
player_walk_image = load_image('Hero/Rogue/Run/Run-Sheet1.png', -1)
enemy_image = load_image('Enemy/Skeleton Crew/Skeleton - Base/Idle/Idle-Sheet.png', -1)
enemy_walk_image = load_image('Enemy/Skeleton Crew/Skeleton - Base/Run/Run-Sheet.png', -1)
quest_background = load_image('Environment/Dungeon Prison/Assets/Quest_Background.png')
bullet_img = load_image('Environment/Dungeon Prison/Assets/bullet.png', -1)
hit_img = load_image('Environment/Dungeon Prison/Assets/hit.png', -1)
tile_images = {
    '1': 'Environment/Dungeon Prison/Assets/Boxwall.png',
    '2': 'Environment/Dungeon Prison/Assets/barrelwall.pngp',
    '3': 'Environment/Dungeon Prison/Assets/Exit.pngp',
    '4': 'Environment/Dungeon Prison/Assets/Jug.pngp'
}


def start_screen():
    global play
    fon = pygame.transform.scale(load_image('Backgrounds/pressbackground.png'), (width, height))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                play = False
                return
            if event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        screen.blit(fon, (0, 0))
        pygame.display.flip()
        clock.tick(10)


def IntoAkk():
    global active, play
    fon = pygame.transform.scale(load_image('Backgrounds/passbackground.png'), (width, height))
    screen.blit(fon, (0, 0))
    text = '********'
    font = pygame.font.Font('Data/Courier.ttf', 150)
    string_rendered = font.render(text, 1, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top, intro_rect.left = 268, 332
    screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    play = False
                    return
                if event.unicode and event.unicode.isalnum() and text[-1] == '*':
                    text = text[:text.find('*')] + event.unicode + text[text.find('*') + 1:]
                    string_rendered = font.render(text, 1, pygame.Color('white'))
                    screen.blit(fon, (0, 0))
                    screen.blit(string_rendered, intro_rect)
            if event.type == pygame.KEYDOWN and text[0] != '*':
                if event.key == pygame.K_BACKSPACE:
                    if text[-1] == '*':
                        text = text[:text.find('*') - 1] + '*' * (8 - text.find('*') + 1)
                    else:
                        text = text[:7] + '*'
                    string_rendered = font.render(text, 1, pygame.Color('white'))
                    screen.blit(fon, (0, 0))
                    screen.blit(string_rendered, intro_rect)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    cur.execute("SELECT COUNT(*) FROM Users WHERE password = ?", (text,))
                    if cur.fetchone()[0]:
                        active = True
                        return
        pygame.display.flip()
        clock.tick(20)


class Menu:
    def __init__(self):
        global active
        self.option_surfaces = []
        self.callbacks = []
        self.args = []
        self.current_option_index = 0

    def append_option(self, option, callback, arg=''):
        self.option_surfaces.append(arial_100.render(option, True, (255, 255, 255)))
        self.callbacks.append(callback)
        self.args.append(arg)

    def switch(self, direction):
        if active:
            self.current_option_index = max(0, min(self.current_option_index + direction,
                                                len(self.option_surfaces) - 1)) # Эта строка предотвращает ошибки с индексом

    def select(self):
        if active:
            if self.args[self.current_option_index] != '':
                self.callbacks[self.current_option_index](self.args[self.current_option_index])
            else:
                self.callbacks[self.current_option_index]()

    def draw(self, x, y, padding):
        if active:
            for i, option in enumerate(self.option_surfaces):
                option_rect = option.get_rect()
                option_rect.topleft = (x, y + i * padding)
                if i == self.current_option_index:
                    pygame.draw.rect(screen, (0, 100, 0), option_rect)
                screen.blit(option, option_rect)


class Tile(pygame.sprite.Sprite):
    def __init__(self, typ, x, y, tile_width, tile_height):
        super().__init__(all_sprites)
        if typ != '3':
            wall_group.add(self)
        else:
            exit_group.add(self)
        if tile_images[typ][-1] == 'p':
            self.image = load_image(tile_images[typ][:-1], -1)
        else:
            self.image = load_image(tile_images[typ])
        self.rect = self.image.get_rect().move(tile_width, tile_height)
        self.rect.topleft = (x, y)


def tile_update(el):
    typ, x, y, w, h = el.split('/')
    Tile(typ, int(x), int(y), int(w), int(h))


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        global game, player_walking
        super().__init__(player_group, all_sprites)
        self.frames_standing = []
        self.frames_walking = []
        self.sheet1 = player_image
        self.sheet2 = player_walk_image
        self.cut_sheet(self.sheet1, 4, 1, self.frames_standing)
        self.cut_sheet(self.sheet2, 6, 1, self.frames_walking)
        self.cur_frame = 0
        self.image = self.frames_standing[self.cur_frame]
        self.rect = self.image.get_rect().move(32, 31)
        self.rect.topleft = (x, y)

    def cut_sheet(self, sheet, columns, rows, frames_list):
        rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (rect.w * i, rect.h * j)
                frames_list.append(sheet.subsurface(pygame.Rect(frame_location, rect.size)))

    def update(self):
        if game:
            if player_walking:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames_walking)
                self.image = self.frames_walking[self.cur_frame]
            else:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames_standing)
                self.image = self.frames_standing[self.cur_frame]
            return self.image


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        global game, enemy_walking
        super().__init__(enemy_group, all_sprites)
        self.health = 100
        self.frames_standing = []
        self.frames_walking = []
        self.sheet1 = enemy_image
        self.sheet2 = enemy_walk_image
        self.cut_sheet(self.sheet1, 4, 1, self.frames_standing)
        self.cut_sheet(self.sheet2, 5, 1, self.frames_walking)
        self.cur_frame = 0
        self.image = self.frames_standing[self.cur_frame]
        self.rect = self.image.get_rect().move(32, 31)
        self.rect.topleft = (x, y)

    def cut_sheet(self, sheet, columns, rows, frames_list):
        rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (rect.w * i, rect.h * j)
                frames_list.append(sheet.subsurface(pygame.Rect(frame_location, rect.size)))

    def update(self):
        if game:
            if enemy_walking:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames_walking)
                self.image = self.frames_walking[self.cur_frame]
            else:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames_standing)
                self.image = self.frames_standing[self.cur_frame]
            return self.image


def create_enemies(settings):
    n, x, y, a, b = map(int, settings.split('/'))
    for i in range(n):
        enemy = Enemy(x + i * a, y + i * b)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(bullet_group, all_sprites)
        self.speed_x = 0
        self.speed_y = 0
        self.speed = 25
        self.frames = []
        self.sheet1 = bullet_img
        self.cut_sheet(self.sheet1, 3, 1, self.frames)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(1, 1)
        self.rect.topleft = (x, y)

    def cut_sheet(self, sheet, columns, rows, frames_list):
        rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (rect.w * i, rect.h * j)
                frames_list.append(sheet.subsurface(pygame.Rect(frame_location, rect.size)))

    def update(self):
        if game:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            return self.image

    def find_path(self, dest_x, dest_y):
        delta_x = dest_x - self.rect.centerx
        delta_y = dest_y - self.rect.centery
        distance = math.sqrt(delta_x ** 2 + delta_y ** 2)

        if distance != 0:
            self.speed_x = (delta_x / distance) * self.speed
            self.speed_y = (delta_y / distance) * self.speed

    def move_to(self):
        global screen, bullet_group, wall_group
        self.rect.left += self.speed_x
        self.rect.top += self.speed_y

        if self.rect.left > 455 and self.rect.right < 995 \
                and self.rect.top > 119 and self.rect.bottom < 710:
            if not pygame.sprite.spritecollideany(self, wall_group):
                return True
        return False


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, sheet, columns, rows):
        super().__init__(particle_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows, self.frames)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(x, y)

    def cut_sheet(self, sheet, columns, rows, frames_list):
        rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (rect.w * i, rect.h * j)
                frames_list.append(sheet.subsurface(pygame.Rect(frame_location, rect.size)))

    def update(self):
        if game:
            if self.cur_frame != 3:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
                return self.image
            else:
                self.kill()



class Game:
    def __init__(self):
        self.end_time = None

    def open_game(self, args):
        global game, active, activeG, els
        game, active, activeG = True, False, False
        self.i, self.folder = args.split(',')
        self.load_map(self.folder, self.i)
        cur2.execute("SELECT setting FROM Mission WHERE number = ?", (self.i,))
        els, self.en_settings = cur2.fetchone()[0].split(';')
        els = els.split(':')
        # 1/753/508/10/9:1/603/545/10/9:3/795/100/40/40:2/600/200/10/9:4/900/290/1/2:4/919/289/1/2;8/550/210/40/50
        # 1/523/568/10/9:1/683/500/10/9:2/513/476/10/9:3/795/100/40/40:2/805/250/10/9:4/534/250/1/2:4/557/260/1/2:4/537/265/1/2:4/560/272/1/2;5/600/250/80/50
        create_enemies(self.en_settings)

    def load_map(self, folder, i):
        global gamefon
        self.path = f'Environment/{folder}/Map{i}.png'
        gamefon = pygame.transform.scale(load_image(self.path), (1000, 720))
        screen.blit(gamefon, (0, 0))

    def game_end(self, i=1):
        global game, active, running
        game = False
        active = True
        player.rect.topleft = (600, 655)
        for sprite in enemy_group:
            sprite.kill()
        self.fon = load_image(f'Backgrounds/End{i}.png')
        self.end_time = pygame.time.get_ticks()
        if i == 1:
            self.font = pygame.font.Font('Data/Courier.ttf', 100)
            self.string_rendered = self.font.render(str(score), 1, pygame.Color('white'))
            self.score_rect = self.string_rendered.get_rect()
            self.score_rect.left, self.score_rect.top = 314, 382

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                    return
            if pygame.time.get_ticks() - self.end_time >= 10000:
                return
            screen.blit(self.fon, (0, 0))
            if i == 1:
                screen.blit(self.string_rendered, self.score_rect)
            pygame.display.flip()
            clock.tick(10)



def Quit():
    global running
    running = False


class GameMenu():
    def __init__(self):
        global activeG, G_current_option_index
        self.option_surfaces = []
        self.callbacks = []
        self.args = []
        G_current_option_index = 0

    def append_option(self, option, callback, arg=''):
        self.option_surfaces.append(arial_100.render(option, True, (255, 255, 255)))
        self.callbacks.append(callback)
        self.args.append(arg)

    def switch(self, direction):
        global G_current_option_index
        if activeG:
            G_current_option_index = max(0, min(G_current_option_index + direction,
                                                len(self.option_surfaces) - 1)) # Эта строка предотвращает ошибки с индексом

    def select(self):
        if activeG:
            if self.args[G_current_option_index] != '':
                self.callbacks[G_current_option_index](self.args[G_current_option_index])
            else:
                self.callbacks[G_current_option_index]()

    def draw(self, x, y, padding):
        if activeG:
            for i, option in enumerate(self.option_surfaces):
                option_rect = option.get_rect()
                option_rect.topleft = (x, y + i * padding)
                if i == G_current_option_index:
                    pygame.draw.rect(screen, (0, 100, 0), option_rect)
                screen.blit(option, option_rect)

    def Back(self):
        global active, activeG, G_current_option_index
        active, activeG = True, False
        G_current_option_index = 0


def OpenSMenu():
    global active, activeG, gamemenu
    active, activeG = False, True


clock = pygame.time.Clock()
start_screen()
if play:
    IntoAkk()
menu = Menu()
gamemenu = GameMenu()
mission = Game()
player = Player(600, 655)
menu.append_option('Играть', OpenSMenu)
menu.append_option('Выход', Quit)
gamemenu.append_option('Миссия 1', mission.open_game, '1,Dungeon Prison/Assets')
gamemenu.append_option('Миссия 2', mission.open_game, '2,Dungeon Prison/Assets')
gamemenu.append_option('Назад', gamemenu.Back)
running = play
enemys_update_timer = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Quit()
        if active:
            if ((event.type == pygame.KEYDOWN)
            and (event.key == pygame.K_w)):
                menu.switch(-1)
            if ((event.type == pygame.KEYDOWN)
            and (event.key == pygame.K_s)):
                menu.switch(1)
            if ((event.type == pygame.KEYDOWN)
            and (event.key == pygame.K_SPACE)):
                menu.select()
        elif activeG:
            if ((event.type == pygame.KEYDOWN)
            and (event.key == pygame.K_w)):
                gamemenu.switch(-1)
            if ((event.type == pygame.KEYDOWN)
            and (event.key == pygame.K_s)):
                gamemenu.switch(1)
            if ((event.type == pygame.KEYDOWN)
            and (event.key == pygame.K_SPACE)):
                gamemenu.select()
        if game:
            m1_cooldown -= 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    nav += 'a'
                    player_walking = True
                elif event.key == pygame.K_w:
                    nav += 'w'
                    player_walking = True
                elif event.key == pygame.K_d:
                    nav += 'd'
                    player_walking = True
                elif event.key == pygame.K_s:
                    nav += 's'
                    player_walking = True
                if event.key == pygame.K_e:
                    if pygame.sprite.spritecollideany(player, exit_group):
                        mission.game_end()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if m1_cooldown <= 0:
                    bullet = Bullet(player.rect.left, player.rect.top)
                    b_coords = pygame.mouse.get_pos()
                    bullet.find_path(b_coords[0], b_coords[1])
                    m1_cooldown = 5

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    nav = nav[:nav.find('a')] + nav[nav.find('a') + 1::]
                elif event.key == pygame.K_w:
                    nav = nav[:nav.find('w')] + nav[nav.find('w') + 1::]
                elif event.key == pygame.K_d:
                    nav = nav[:nav.find('d')] + nav[nav.find('d') + 1::]
                elif event.key == pygame.K_s:
                    nav = nav[:nav.find('s')] + nav[nav.find('s') + 1::]

    screen.fill((0, 0, 0))
    if active:
        menu.draw(100, 100, 100)
    elif activeG:
        gamemenu.draw(100, 100, 100)
    elif game:
        screen.blit(gamefon, (0, 0))
        for bullet in bullet_group:
            if not bullet.move_to():
                bullet.kill()
            else:
                for enemy in enemy_group:
                    hit_enemy_group.add(enemy)
                    if pygame.sprite.spritecollideany(bullet, hit_enemy_group):
                        particle = Particle(bullet.rect.left, bullet.rect.top, hit_img, 4, 1)
                        enemy.health -= 20
                        bullet.kill()
                        if enemy.health <= 0:
                            score += 20
                            enemy.kill()
                    hit_enemy_group.remove(enemy)

        for el in els:
            tile_update(el)

        if nav != '':
            for el in nav:
                if el == 'a':
                    player.rect.left -= 10
                    if pygame.sprite.spritecollideany(player, wall_group):
                        player.rect.left += 10
                    elif player.rect.left < 455:
                        player.rect.left = 455

                if el == 'd':
                    player.rect.left += 10
                    if pygame.sprite.spritecollideany(player, wall_group):
                        player.rect.left -= 10
                    elif player.rect.right > 995:
                        player.rect.right = 995

                if el == 'w':
                    player.rect.top -= 10
                    if pygame.sprite.spritecollideany(player, wall_group):
                        player.rect.top += 10
                    elif player.rect.top < 119:
                        player.rect.top = 119

                if el == 's':
                    player.rect.top += 10
                    if pygame.sprite.spritecollideany(player, wall_group):
                        player.rect.top -= 10
                    elif player.rect.bottom > 710:
                        player.rect.bottom = 710
        else:
            player_walking = False

        enemy_update_interval = random.randint(1, 3)
        enemys_update_timer += 1

        if enemys_update_timer >= enemy_update_interval:
            enemys_update_timer = 0

            for enemys in enemy_group:
                action = random.choice(['Idle', 'Run'])
                if action == 'Idle':
                    enemy_walking = False
                else:
                    move = random.choice(['W', 'A', 'S', 'D'])
                    enemy_walking = True
                    enemy_speed = random.randint(8, 15)

                    if move == 'W':
                        enemys.rect.top -= enemy_speed
                        if pygame.sprite.spritecollideany(enemys, wall_group):
                            enemys.rect.top += enemy_speed
                        elif enemys.rect.top < 119:
                            enemys.rect.top = 119
                    elif move == 'S':
                        enemys.rect.top += enemy_speed
                        if pygame.sprite.spritecollideany(enemys, wall_group):
                            enemys.rect.top -= enemy_speed
                        elif enemys.rect.bottom > 710:
                            enemys.rect.bottom = 710
                    elif move == 'A':
                        enemys.rect.left -= enemy_speed
                        if pygame.sprite.spritecollideany(enemys, wall_group):
                            enemys.rect.left += enemy_speed
                        elif enemys.rect.left < 455:
                            enemys.rect.left = 455
                    else:
                        enemys.rect.left += enemy_speed
                        if pygame.sprite.spritecollideany(enemys, wall_group):
                            enemys.rect.left -= enemy_speed
                        elif enemys.rect.right > 995:
                            enemys.rect.right = 995
                if pygame.sprite.spritecollideany(enemys, player_group):
                    mission.game_end(2)

        all_sprites.update()
        all_sprites.draw(screen)
        player_group.draw(screen)
        enemy_group.draw(screen)
        particle_group.draw(screen)

    pygame.display.flip()
    clock.tick(10)
conn1.close()
conn2.close()
pygame.quit()