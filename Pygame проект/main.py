import os
import sys
import random

import pygame
import sqlite3

pygame.init()
screen_info = pygame.display.Info()
pygame.display.set_caption("IMperfect World")
conn2 = sqlite3.connect('Data/Settings.db')
cur2 = conn2.cursor()
size = width, height = 1366, 768
cur2.execute("SELECT sizes FROM Objects WHERE screen_info = ?", ('1',))
els = cur2.fetchone()[0].split(':')
conn2.close()
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
tile_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
conn1 = sqlite3.connect('Data/data-iw.db')
cur = conn1.cursor()
arial_100 = pygame.font.SysFont('arial', 100)
nav = ''
quest = 'Сбеги через дверь!'
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
        super().__init__(tile_group, all_sprites)
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
    # 1/523/568/10/9:1/683/500/10/9:2/513/476/10/9:3/795/100/40/40:2/805/250/10/9:4/534/250/1/2:4/557/260/1/2:4/537/265/1/2:4/560/272/1/2


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


def create_enemies():
    for i in range(5):  # Создаем 5 врагов
        enemy = Enemy(600 + i * 80, 250)  # Начальная позиция врагов


class Game:
    def __init__(self):
        self.end_time = None

    def open_game(self, args):
        global game, active, activeG, player
        game, active, activeG = True, False, False
        i, folder = args.split(',')
        self.load_map(folder, i)
        create_enemies()

    def load_map(self, folder, i):
        global gamefon
        self.path = f'Environment/{folder}/Map{i}.png'
        gamefon = pygame.transform.scale(load_image(self.path), (1000, 720))
        screen.blit(gamefon, (0, 0))

    def game_end(self, score, i=1):
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
            self.string_rendered = self.font.render(score, 1, pygame.Color('white'))
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
gamemenu.append_option('Назад', gamemenu.Back)
# player, level_x, level_y = generate_level(load_level('map.txt'))
running = play
enemys_update_timer = 0
Qfont = pygame.font.SysFont('arial', 42)
Qstring_rendered = Qfont.render(quest, 1, pygame.Color('black'))
Quest_rect = Qstring_rendered.get_rect()
Quest_rect.left, Quest_rect.top = 35, 68
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
                        mission.game_end('100')

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
        screen.blit(quest_background, (20, 50))
        screen.blit(Qstring_rendered, Quest_rect)

        for el in els:
            tile_update(el)
        clock.tick(12)

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

        enemy_update_interval = random.randint(1, 4)
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
                    enemy_speed = random.randint(15, 25)

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
                    mission.game_end('000', 2)

        all_sprites.update()
        all_sprites.draw(screen)
        player_group.draw(screen)
        enemy_group.draw(screen)

    pygame.display.flip()
    clock.tick(60)
conn1.close()
pygame.quit()