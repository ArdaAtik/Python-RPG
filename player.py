import pygame
from settings import *
from os import walk
from debug import debug

from support import import_folder


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_weapon, create_magic):
        super().__init__(groups)
        self.image = pygame.image.load('./graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.obstacle_sprites = obstacle_sprites
        self.hitbox = self.rect.inflate(0, -26)  # watch YouTube
        # movement
        self.direction = pygame.math.Vector2()
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = 0
        # weapon
        self.weapon_index = 1
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.create_attack = create_attack
        self.destroy_weapon = destroy_weapon
        self.can_switch_weapon = True
        self.weapon_switch_time = 0
        self.switch_cooldown = 200

        # magic
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.weapon_index]
        self.can_switch_magic = True
        self.magic_switch_time = 0

        # graphics setup
        self.status = 'down'
        self.import_player_assets()
        self.frame_index = 0
        self.animation_speed = 0.15

        # stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 6}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.exp = 132
        self.speed = self.stats['speed']

    def get_status(self):
        # idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = self.status + '_idle'
            # if 'attack' in self.status and self.attacking is False:
            #     self.status = self.status.replace('_attack', '_idle')

        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '_idle')

    def input(self):
        if not self.attacking:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0

            # attacks input
            if keys[pygame.K_SPACE] and not self.attacking:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()
            if keys[pygame.K_LCTRL] and not self.attacking:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                style = list(magic_data.keys())[self.magic_index]
                strength = list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic']
                cost = list(magic_data.values())[self.magic_index]['cost']
                self.create_magic(style, strength, cost)
            if keys[pygame.K_q] and self.can_switch_weapon:
                if self.weapon_index < len(list(weapon_data.keys())) - 1:
                    self.weapon_index += 1
                else:
                    self.weapon_index = 0
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
                self.weapon = list(weapon_data.keys())[self.weapon_index]
                print(self.weapon_index)
                print(self.weapon)

            if keys[pygame.K_e] and self.can_switch_magic:
                if self.magic_index < len(list(magic_data.keys())) - 1:
                    self.magic_index += 1
                else:
                    self.magic_index = 0
                self.can_switch_magic = False
                self.magic_switch_time = pygame.time.get_ticks()
                self.magic = list(magic_data.keys())[self.magic_index]
                print(self.magic_index)
                print(self.magic)

    def import_player_assets(self):
        character_path = './graphics/player/'
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
            'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []
        }
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)
        print(self.animations)

    def move(self, speed):

        if self.direction.magnitude() > 1:
            self.direction = self.direction.normalize()
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')

        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')

        self.rect.center = self.hitbox.center
        # self.rect.center += self.direction * speed

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    elif self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom

    def cooldowns(self):
        current_time = pygame.time.get_ticks()  # 120
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_weapon()
        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_cooldown:
                self.can_switch_weapon = True
        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_cooldown:
                self.can_switch_magic = True

    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index > len(animation):
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def update(self):
        self.cooldowns()
        self.input()
        self.move(self.speed)
        self.get_status()
        self.animate()
