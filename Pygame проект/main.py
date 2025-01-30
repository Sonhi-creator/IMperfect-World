import os
import sys

import pygame
import sqlite3

pygame.init()
screen_info = pygame.display.Info()
size = width, height = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode(size)
menu = None
all_sprites = pygame.sprite.Group()
tile_width = tile_height = 50
tile_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
player = pygame.sprite.Group()
conn = sqlite3.connect('Data/data-iw.db')
cur = conn.cursor()
arial_100 = pygame.font.SysFont('arial', 100)
active = False
activeG = False


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


# tile_images = {
#     'wall': load_image('box.png'),
#     'empty': load_image('grass.png')
# }
# player_image = load_image('mar.png')


def start_screen():
    fon = pygame.transform.scale(load_image('Backgrounds/pressbackground.png'), (width, height))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        screen.blit(fon, (0, 0))
        pygame.display.flip()
        clock.tick(10)


def IntoAkk():
    global menu, active
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
                        menu = Menu()
                        active = True
                        return
        pygame.display.flip()
        clock.tick(20)


class Menu:
    def __init__(self):
        global active
        self.option_surfaces = []
        self.callbacks = []
        self.current_option_index = 0

    def append_option(self, option, callback):
        if active:
            self.option_surfaces.append(arial_100.render(option, True, (255, 255, 255)))
            self.callbacks.append(callback)

    def switch(self, direction):
        if active:
            self.current_option_index = max(0, min(self.current_option_index + direction,
                                                len(self.option_surfaces) - 1)) # Эта строка предотвращает ошибки с индексом

    def select(self):
        if active:
            self.callbacks[self.current_option_index]()

    def draw(self, x, y, padding):
        if active:
            for i, option in enumerate(self.option_surfaces):
                option_rect = option.get_rect()
                option_rect.topleft = (x, y + i * padding)
                if i == self.current_option_index:
                    pygame.draw.rect(screen, (0, 100, 0), option_rect)
                screen.blit(option, option_rect)


# class Tile(pygame.sprite.Sprite):
#     def __init__(self, typ, x, y):
#         super().__init__(tile_group, all_sprites)
#         self.image = tile_images[typ]
#         if typ == 'wall':
#             wall_group.add(self)
#         self.rect = self.image.get_rect().move(tile_width * x,
#                                                tile_height * y)


# class Player(pygame.sprite.Sprite):
#     def __init__(self, x, y):
#         super().__init__(tile_group, all_sprites)
#         self.image = player_image
#         self.rect = self.image.get_rect().move(tile_width * x + 15,
#                                                tile_height * y + 5)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def Quit():
    global running
    running = False


class GameMenu():
    def __init__(self):
        global activeG
        self.option_surfaces = []
        self.callbacks = []
        self.current_option_index = 0

    def append_option(self, option, callback):
        if activeG:
            self.option_surfaces.append(arial_100.render(option, True, (255, 255, 255)))
            self.callbacks.append(callback)

    def switch(self, direction):
        if activeG:
            self.current_option_index = max(0, min(self.current_option_index + direction,
                                                len(self.option_surfaces) - 1)) # Эта строка предотвращает ошибки с индексом

    def select(self):
        if activeG:
            self.callbacks[self.current_option_index]()

    def draw(self, x, y, padding):
        if activeG:
            for i, option in enumerate(self.option_surfaces):
                option_rect = option.get_rect()
                option_rect.topleft = (x, y + i * padding)
                if i == self.current_option_index:
                    pygame.draw.rect(screen, (0, 100, 0), option_rect)
                screen.blit(option, option_rect)

    def Back(self):
        global active, activeG
        active, activeG = True, False


def OpenSMenu():
    global active, activeG, gamemenu
    active, activeG = False, True
    gamemenu = GameMenu()
    gamemenu.append_option('Миссия 1', Quit)
    gamemenu.append_option('Назад', gamemenu.Back)


# player = None
clock = pygame.time.Clock()
start_screen()
IntoAkk()
menu = Menu()
gamemenu = GameMenu()
menu.append_option('Играть', OpenSMenu)
menu.append_option('Выход', Quit)
gamemenu.append_option('Миссия 1', Quit)
gamemenu.append_option('Назад', gamemenu.Back)
# player, level_x, level_y = generate_level(load_level('map.txt'))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
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
        # if player is not None:
        #     if pygame.sprite.spritecollideany(player, wall_group) is None:
        #         if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
        #             player.rect.top -= 50
        #             if pygame.sprite.spritecollideany(player, wall_group):
        #                 player.rect.top += 50
        #     if pygame.sprite.spritecollideany(player, wall_group) is None:
        #         if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
        #             player.rect.right -= 50
        #             if pygame.sprite.spritecollideany(player, wall_group):
        #                 player.rect.right += 50
        #     if pygame.sprite.spritecollideany(player, wall_group) is None:
        #         if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
        #             player.rect.right += 50
        #             if pygame.sprite.spritecollideany(player, wall_group):
        #                 player.rect.right -= 50
        #     if pygame.sprite.spritecollideany(player, wall_group) is None:
        #         if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
        #             player.rect.top += 50
        #             if pygame.sprite.spritecollideany(player, wall_group):
        #                 player.rect.top -= 50
    screen.fill((0, 0, 0))
    if active:
        menu.draw(100, 100, 100)
    elif activeG:
        gamemenu.draw(100, 100, 100)
    # all_sprites.draw(screen)
    # all_sprites.update()
    # tile_group.draw(screen)
    # tile_group.update(screen)
    pygame.display.flip()
    clock.tick(60)
conn.close()
pygame.quit()