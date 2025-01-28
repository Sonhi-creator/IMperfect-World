import os
import sys

import pygame
import sqlite3

pygame.init()
screen_info = pygame.display.Info()
size = width, height = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
tile_width = tile_height = 50
tile_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
player = pygame.sprite.Group()
conn = sqlite3.connect('Data/data-iww.db')
cur = conn.cursor()


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
    fon = pygame.transform.scale(load_image('Backgrounds\pressbackground.png'), (width, height))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return IntoAkk()
        pygame.display.flip()
        clock.tick(10)


def IntoAkk():
    fon = pygame.transform.scale(load_image('Backgrounds\passbackground.png'), (width, height))
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
            elif event.type == pygame.KEYDOWN:
                if event.unicode and event.unicode.isalnum() and text[-1] == '*':
                    text = text[:text.find('*')] + event.unicode + text[text.find('*') + 1:]
                    string_rendered = font.render(text, 1, pygame.Color('white'))
                    screen.blit(fon, (0, 0))
                    screen.blit(string_rendered, intro_rect)
                elif event.type == pygame.KEYDOWN and text[0] != '*':
                    if event.key == pygame.K_BACKSPACE:
                        if text[-1] == '*':
                            text = text[:text.find('*') - 1] + '*' * (8 - text.find('*') + 1)
                        else:
                            text = text[:7] + '*'
                        string_rendered = font.render(text, 1, pygame.Color('white'))
                        screen.blit(fon, (0, 0))
                        screen.blit(string_rendered, intro_rect)
                elif event.type == pygame.KEYDOWN and text[-1] != '*':
                    if event.key == pygame.K_RETURN:
                        cur.execute("SELECT COUNT(*) FROM Users WHERE password = ?", (text,))
                        if cur.fetchone()[0]:
                            return
        pygame.display.flip()
        clock.tick(20)


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


# def generate_level(level):
#     new_player, x, y = None, None, None
#     for y in range(len(level)):
#         for x in range(len(level[y])):
#             if level[y][x] == '.':
#                 Tile('empty', x, y)
#             elif level[y][x] == '#':
#                 Tile('wall', x, y)
#             elif level[y][x] == '@':
#                 Tile('empty', x, y)
#                 new_player = Player(x, y)
#     return new_player, x, y


# player = None
clock = pygame.time.Clock()
start_screen()
IntoAkk()
# player, level_x, level_y = generate_level(load_level('map.txt'))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
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
    clock.tick(50)
    screen.fill((0, 0, 255))
    # all_sprites.draw(screen)
    # all_sprites.update()
    # tile_group.draw(screen)
    # tile_group.update(screen)
    pygame.display.flip()
conn.close()
pygame.quit()