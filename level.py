import pygame

from magic import Magic
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import import_csv_layout, import_folder
from random import randint

from ui import UI
from weapon import Weapon


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        print(self.display_surface)
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.create_map()
        self.current_attack = None

        # user Interace
        self.ui = UI()

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites])

    def destroy_weapon(self):
        if self.current_attack:
            self.current_attack.kill()

    def create_magic(self, style, strength, cost):
        self.current_attack = Magic(self.player, [self.visible_sprites])

    def create_map(self):
        layout = {
            'boundary': import_csv_layout('./map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('./map/map_Grass.csv'),
            'object': import_csv_layout('./map/map_Objects.csv')
        }
        graphics = {
            'grass': import_folder('./graphics/grass'),
            'objects': import_folder('./graphics/objects')
        }
        for style, layout in layout.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x, y), [self.obstacle_sprites], 'invisible')
                        if style == 'grass':
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'grass',
                                 graphics['grass'][randint(0, 2)])
                        if style == 'object':
                            surf = graphics['objects'][int(col)]
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'object',
                                 surf)
            #         if col == 'x':
            #             Tile((x, y), [self.visible_sprites, self.obstacle_sprites])
            #         if col == 'p':
            #             self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites)
        self.player = Player((2000, 1430), [self.visible_sprites], self.obstacle_sprites, self.create_attack,
                             self.destroy_weapon, self.create_magic)

    def run(self):
        # draw the game
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.ui.display(self.player)


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super(YSortCameraGroup, self).__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        self.floor_surface = pygame.image.load('./graphics/tilemap/ground.png').convert()
        self.floor_rect = self.floor_surface.get_rect(topleft=(0, 0))

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height
        # for sprite in self.sprites():
        offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surface, offset_pos)
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)
