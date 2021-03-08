# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 11:42:17 2020

@author: Anthony Campana
"""

import pygame 
from pygame.sprite import Sprite

class Bullet(Sprite):
    """Aclass to manage bullets fired from the ship"""
    
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color 
        
        #Create a bullet rect at (0,0) and then set correct position.
        #initalizing a bullet rectangle object
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width, self.settings.bullet_height)
        #set the buellets midtop attribute to the ship midbottom attribute
        self.rect.midtop = ai_game.ship.rect.midtop
        
        #Store the bulle's position as a decimal value.
        self.y = float(self.rect.y)
        
    def update(self):
        """Move the bullet up the screen"""
        #Update the decimal positio of the bullet.
        self.y -= self.settings.bullet_speed
        #Update the rect position.
        self.rect.y = self.y
        
    def draw_bullet(self):
        """Draw the bullet to the screen."""
        pygame.draw.rect(self.screen, self.color,self.rect)