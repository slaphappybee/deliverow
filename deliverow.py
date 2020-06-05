# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pygame
from pygame import Surface
from typing import List
import os
import time
import math

DOWN = (0, 1)
UP = (0, -1)
LEFT = (-1, 0)
RIGHT = (1, 0)

dialogues = {
    (12, 20): ["Hi there, I'm Chris."],
    (6, 23): ["Hey. I'm Brian the fisherman."],
    (17, 9): ["Hi, I'm Alice and this is my grampa.", "He's drunk again."],
    (30, 8): ["The name's Balthazar."],
    (31, 25): ["Good morning! I'm Cunaigond.", "I work at the shop."]
}

pygame.font.init() 
comic_sans = pygame.font.SysFont('Comic Sans MS', 30)

def cut_strip(image: Surface, length: int) -> List[Surface]:
    surfaces = list()

    for i in range(0, length):
        s = Surface([16, 16])
        s.set_colorkey((255, 255, 255))
        s.blit(image, (0, 0), pygame.Rect(0, 16 * i, 16, 16))
        surfaces.append(s)

    return surfaces

def cut_character_sprite(image):
    down, up, left, wdown, wup, wleft = cut_strip(image, 6)
    
    result = dict()
    result[(DOWN, 0)] = pygame.transform.scale(down, (64, 64))
    result[(UP, 0)] = pygame.transform.scale(up, (64, 64))
    result[(LEFT, 0)] = pygame.transform.scale(left, (64, 64))
    result[(RIGHT, 0)] = pygame.transform.flip(result[(LEFT, 0)], True, False)
    result[(DOWN, 1)] = pygame.transform.scale(wdown, (64, 64))
    result[(UP, 1)] = pygame.transform.scale(wup, (64, 64))
    result[(LEFT, 1)] = pygame.transform.scale(wleft, (64, 64))
    result[(RIGHT, 1)] = pygame.transform.flip(result[(LEFT, 1)], True, False)
    result[(DOWN, 2)] = result[(DOWN, 0)]
    result[(UP, 2)] = result[(UP, 0)]
    result[(LEFT, 2)] = result[(LEFT, 0)]
    result[(RIGHT, 2)] = result[(RIGHT, 0)]
    result[(DOWN, 3)] = pygame.transform.flip(result[(DOWN, 1)], True, False)
    result[(UP, 3)] = pygame.transform.flip(result[(UP, 1)], True, False)
    result[(LEFT, 3)] = result[(LEFT, 1)]
    result[(RIGHT, 3)] = result[(RIGHT, 1)]
    
    return result

def load_sprite(name: str):
    surface = pygame.image.load(os.path.join('pokered', 'gfx', 'sprites', name + '.png'))
    sprites = cut_character_sprite(surface)
    return sprites

lass_sprites = load_sprite('lass')
daisy_sprites = load_sprite('daisy')

world_map = pygame.image.load(os.path.join('pic', 'city.png'))
world_map = pygame.transform.scale(
        world_map, (world_map.get_width() * 4, world_map.get_height() * 4))

with open(os.path.join('pic', 'city.map')) as f:
    terrain_def = f.readlines()


class ActorCollection(object):
    def __init__(self):
        self.items = list()

    def is_free(self, dest):
        return not any(i.position == dest for i in self.items)


actors = ActorCollection()


class PlayerCharacter(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = lass_sprites[(DOWN, 0)]
        
        self.rect = self.image.get_rect()
        self.position = (6, 4)
        self.facing = DOWN
        self.rect.x = 64 * self.position[0]
        self.rect.y = (64 * self.position[1]) - (4 * 4)
        self.timeout = 0
        self.animation_state = 0
    
    def can_go(self, dest):
        return terrain_def[dest[1]][dest[0]] == ' ' and actors.is_free(dest)

    def go(self, dest):
        self.position = dest

    def animate(self):
        self.timeout = 8

    def update(self):
        if self.timeout > 0:
            self.timeout -= 1
            idx_animation = math.floor(self.timeout / 4) % 4
            idx_modifier = 2 * self.animation_state
            self.image = lass_sprites[(self.facing, idx_animation + idx_modifier)]

            if self.timeout == 0:
                self.animation_state = not self.animation_state
    
    def face(self, direction):
        self.facing = direction
        self.image = lass_sprites[(self.facing, 0)]
    
    def get_facing(self):
        return self.facing[0] + self.position[0], \
            self.facing[1] + self.position[1]

class Character(pygame.sprite.Sprite):
    def __init__(self, sprite, position):
        pygame.sprite.Sprite.__init__(self)
        self.sprite = sprite
        self.image = self.sprite[(DOWN, 0)]

        self.rect = self.image.get_rect()
        self.position = position
        self.facing = DOWN
        self.rect.x = 64 * self.position[0]
        self.rect.y = (64 * self.position[1]) - (4 * 4)


class Viewport():
    def __init__(self):
        self.sprites = list()
        self.velocity = (0, 0)
        self.timeout = 0
    
    def add(self, sprite):
        self.sprites.append(sprite)

    def init_move(self, velocity):
        self.velocity = velocity
        self.timeout = 8 

    def is_moving(self):
        return self.velocity != (0, 0)

    def update(self):
        if self.timeout > 0:
            for sprite in self.sprites:
                sprite.rect.x += 8 * self.velocity[0]
                sprite.rect.y += 8 * self.velocity[1]
            self.timeout -= 1
            if self.timeout == 0:
                self.velocity = (0, 0)


class Terrain(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = world_map
        self.rect = self.image.get_rect()


class Dialogue(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.timeout = 0
        self.hide()
        self.dialogue = []
        
    def set_text(self, text):
        self.image = comic_sans.render(text, False, (0, 0, 0), 
                                       pygame.Color("white"))
        self.rect = self.image.get_rect()
        self.rect.x = 3 * 64
        self.rect.y = 8 * 64
        self.timeout = 16
    
    def set_dialogue(self, dialogue):
        self.dialogue = dialogue
        self.set_text(dialogue[0])
    
    def scroll(self):
        if len(self.dialogue) > 0:
            self.set_text(self.dialogue[0])
            self.dialogue = self.dialogue[1:]
        else:
            self.hide()
        
    def visible(self):
        return self.image.get_width() > 0
    
    def hide(self):
        self.image = pygame.Surface([0, 0])
        self.rect = self.image.get_rect()
        self.timeout = 16
    
    def update(self):
        if self.timeout > 0:
            self.timeout -= 1
    
    
playerCharacter = PlayerCharacter()
daisyCharacter = Character(daisy_sprites, (8, 20))
actors.items.append(daisyCharacter)
terrain = Terrain()
viewport = Viewport()
viewport.add(terrain)
viewport.add(daisyCharacter)
dialogue = Dialogue()

characters = pygame.sprite.Group(playerCharacter, daisyCharacter)
background = pygame.sprite.Group(terrain)
overlay = pygame.sprite.Group(dialogue)

pygame.init()

gameDisplay = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Kanto")

game_exit = False

move_mapping = {
    pygame.K_UP: (0, 1),
    pygame.K_DOWN: (0, -1),
    pygame.K_LEFT: (1, 0),
    pygame.K_RIGHT: (-1, 0)
}

while not game_exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_exit = True
            
    pressed = pygame.key.get_pressed()
    if not viewport.is_moving() and not dialogue.visible():
        for key in move_mapping.keys():
            if pressed[key]:
                shift = move_mapping[event.key]
                dest_x = playerCharacter.position[0] - shift[0]
                dest_y = playerCharacter.position[1] - shift[1]
                playerCharacter.face((-shift[0], -shift[1]))
                if playerCharacter.can_go((dest_x, dest_y)):
                    viewport.init_move(shift)
                    playerCharacter.animate()
                    playerCharacter.go((dest_x, dest_y))
                break
    
    if pressed[pygame.K_RETURN] and dialogue.timeout == 0:
        if not dialogue.visible():
            facing = playerCharacter.get_facing()
            if facing in dialogues:
                dialogue.set_dialogue(dialogues[facing])
        else:
            dialogue.scroll()
    
    viewport.update()
    background.update()
    overlay.update()
    playerCharacter.update()
    background.draw(gameDisplay)
    characters.draw(gameDisplay)
    overlay.draw(gameDisplay)
    pygame.display.update()
    time.sleep(0.01)

pygame.quit()
quit()
