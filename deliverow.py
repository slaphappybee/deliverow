# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pygame
import os

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

def cut_character_sprite(image):
    result = dict()
    
    pic_down = pygame.Surface([16, 16])
    pic_down.set_colorkey((0, 255, 0))
    pic_down.blit(image, (0, 0), pygame.Rect(0, 0, 16, 16))
    result[DOWN] = pygame.transform.scale(pic_down, (64, 64))
    
    pic_up = pygame.Surface([16, 16])
    pic_up.set_colorkey((0, 255, 0))
    pic_up.blit(image, (0, 0), pygame.Rect(0, 16, 16, 16))
    result[UP] = pygame.transform.scale(pic_up, (64, 64))
    
    pic_left = pygame.Surface([16, 16])
    pic_left.set_colorkey((0, 255, 0))
    pic_left.blit(pic_lass, (0, 0), pygame.Rect(0, 32, 16, 16))
    result[LEFT] = pygame.transform.scale(pic_left, (64, 64))
    
    result[RIGHT] = pygame.transform.flip(result[LEFT], True, False)
    
    return result

pic_lass = pygame.image.load(os.path.join('pic', 'lass.png'))
lass_sprites = cut_character_sprite(pic_lass)

world_map = pygame.image.load(os.path.join('pic', 'city.png'))
world_map = pygame.transform.scale(
        world_map, (world_map.get_width() * 4, world_map.get_height() * 4))

with open(os.path.join('pic', 'city.map')) as f:
    terrain_def = f.readlines()
    
class PlayerCharacter(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = lass_sprites[DOWN]
        
        self.rect = self.image.get_rect()
        self.position = (6, 4)
        self.facing = DOWN
        self.rect.x = 64 * 6
        self.rect.y = (64 * 4)  # - (4 * 4)
    
    def can_go(self, dest):
        return terrain_def[dest[1]][dest[0]] == ' '

    def go(self, dest):
        self.position = dest
    
    def face(self, direction):
        self.facing = direction
        self.image = lass_sprites[self.facing]
    
    def get_facing(self):
        return self.facing[0] + self.position[0], \
            self.facing[1] + self.position[1]

class Terrain(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = world_map
        self.rect = self.image.get_rect()
        self.velocity = (0, 0)
        self.move_counter = 0
        
    def is_moving(self):
        return self.velocity != (0, 0)
    
    def init_move(self, velocity):
        self.velocity = velocity
        self.move_counter = 8
    
    def update(self):
        if self.move_counter > 0:
            self.rect.x += 8 * self.velocity[0]
            self.rect.y += 8 * self.velocity[1]
            self.move_counter -= 1
            if self.move_counter == 0:
                self.velocity = (0, 0)


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
terrain = Terrain()
dialogue = Dialogue()

characters = pygame.sprite.Group(playerCharacter)
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
    if not terrain.is_moving() and not dialogue.visible():
        for key in move_mapping.keys():
            if pressed[key]:
                shift = move_mapping[event.key]
                dest_x = playerCharacter.position[0] - shift[0]
                dest_y = playerCharacter.position[1] - shift[1]
                playerCharacter.face((-shift[0], -shift[1]))
                if playerCharacter.can_go((dest_x, dest_y)):
                    terrain.init_move(shift)
                    playerCharacter.go((dest_x, dest_y))
                break
    
    if pressed[pygame.K_RETURN] and dialogue.timeout == 0:
        if not dialogue.visible():
            facing = playerCharacter.get_facing()
            if facing in dialogues:
                dialogue.set_dialogue(dialogues[facing])
        else:
            dialogue.scroll()
            
    background.update()
    overlay.update()
    background.draw(gameDisplay)
    characters.draw(gameDisplay)
    overlay.draw(gameDisplay)
    pygame.display.update()

pygame.quit()
quit()
