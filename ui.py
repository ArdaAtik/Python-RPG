import pygame
from settings import *


class UI:
    def __init__(self):
        # general info
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # bar setup
        self.health_bar_rect = pygame.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        self.energy_bar_rect = pygame.Rect(10, 34, ENERGY_BAR_WIDTH, BAR_HEIGHT)

        # convert dict to list
        self.weapon_graphics = [pygame.image.load(weapon['graphic']).convert_alpha() for weapon in weapon_data.values()]
        self.magic_graphics = [pygame.image.load(magic['graphic']).convert_alpha() for magic in magic_data.values()]
        print(self.magic_graphics, 'magic graphics')

    def show_bar(self, current, max_amount, bg_rect, color):
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width
        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def show_exp(self, exp):
        text_surf = self.font.render(f'{int(exp)}', False, TEXT_COLOR)
        text_rect = text_surf.get_rect(bottomright=(WIDTH - 20, HEIGTH - 20))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(20, 20))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(20, 20), 3)

    def selection_box(self, left, top, has_switched):
        bg_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        if not has_switched:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

        return bg_rect

    def weapon_overlay(self, x, y, weapon_index, has_switched):
        bg_rect = self.selection_box(x, y, has_switched)
        weapon_surface = self.weapon_graphics[weapon_index]
        weapon_rect = weapon_surface.get_rect(center=bg_rect.center)
        self.display_surface.blit(weapon_surface, weapon_rect)

    def magic_overlay(self, x, y, magic_index, has_switched):
        bg_rect = self.selection_box(x, y, has_switched)
        magic_surface = self.magic_graphics[magic_index]
        magic_rect = magic_surface.get_rect(center=bg_rect.center)
        self.display_surface.blit(magic_surface, magic_rect)

    def display(self, player):
        self.show_bar(player.health, player.stats['health'], self.health_bar_rect, HEALTH_COLOR)
        self.show_bar(player.energy, player.stats['energy'], self.energy_bar_rect, ENERGY_COLOR)
        self.show_exp(player.exp)
        self.weapon_overlay(70, 635, player.weapon_index, player.can_switch_weapon)
        self.magic_overlay(10, 630, player.magic_index, player.can_switch_magic)
