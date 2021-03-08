# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 14:42:20 2020

@author: Anthony Campana
"""

import pygame
from pygame.sprite import Sprite

class Ship(Sprite):
    """A calss to manage a ship"""
    def __init__(self, ai_game):
        """Initialize the ship and set its starting position"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()
        
        #load the ship image and gets its rect.
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()
        
        #Start each new ship at the bottom center of the screen.
        self.rect.midbottom = self.screen_rect.midbottom
        
        #Store a decimal value for the ship's horizontal position.
        self.x = float(self.rect.x)
        
        #Movement flag 
        #when false the ship is motionless.
        self.moving_right = False
        self.moving_left = False 
        
    def update(self):
        """Update the ship's posistion based on the movement flag."""
        #update the ship's x value, not the rect.
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        
        #Update rect object from self.x
        self.rect.x = self.x
        
    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)
        
    def center_ship(self):
        """Center the ship on the screen."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)