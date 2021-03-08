# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 11:27:20 2020

@author: Anthony Campana
"""

#Use tools from sys to exit the game
import sys  
import pygame
from time import sleep

from settings import Settings 
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:
    """Overall class to manage game assest and behavior."""
    
    def __init__(self):
        """Initialize the game, and create game resources."""
        #Initalizes the background settings for the game
        pygame.init()
        self.settings = Settings()
        
        #Setting a full screen size for the game
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        #Updating the setings object with the fullscren size 
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        
        #Creats a display window for the game using the dimension defined in the tuple
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")
        #Create an instance to store game statistics, and create a scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        #Making an instance of a ship after the screen has been created 
        self.ship = Ship(self)
        #Manages the bullets on the screen
        self.bullets = pygame.sprite.Group()
        #Creating a group to hold the alien fleet 
        self.aliens = pygame.sprite.Group()
        
        self._create_fleet()
        
        #Make the play button
        self.play_button = Button(self, "Play")
        
    def run_game(self):
        """Start the main loop for the game"""
        while True:
            self._check_events()
            
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            
            self._update_screen()
            
            #displays teh current screen ontop of the last 
            pygame.display.flip()
            
    def _check_events(self):
        """Respond to keypressand mouse events."""
        #Watch for keyboard and mouse events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                
    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            #Reset the game settings.
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            
            #Get rid of any remaining aliens and bullets.
            self.aliens.empty
            self.bullets.empty()
            
            #Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            
            #Hide the mouse cursor.
            pygame.mouse.set_visible(False)
        else:
            pygame.mouse.set_visible(True)
                    
    def _check_keydown_events(self, event):
        #checks what key was pressed and takes action after detecting what key was pressed.
        if event.key == pygame.K_RIGHT: 
            #checkes to see if the key that was pressed was the right arrow key.
            #sets the ship movement to true that moves the ship to right until it is stopped being pressed which sets movement to false.
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
    
    def _check_keyup_events(self, event):
        #detects when the right arrow key is released when being pressed.
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        
    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
    
    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        #Update bullet position.
        self.bullets.update()
            
        #Get rid of bullets that arent on the screen anymore 
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
                
        self._check_bullet_alien_collisions()
        
    def _check_bullet_alien_collisions(self):   
        """Respond to bullet-alien collisions"""
        #Remove any bullets and aliens that collided.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
        
        if not self.aliens:
            #Destroy existing bullets and create new fleet>
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            
            #Increase level.
            self.stats.level += 1
            self.sb.prep_level()
                
        #check for any bullets that have hit aliens.
        #If so, get rid of the bullet and the alien.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
                
    def _update_aliens(self):
        """Check if the fleet is at an edge, then update the positions of all aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()
        
        #Look for alien-ship collisions.
        #takes a sprite and a group.     q
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        
        #Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()
                
    def _create_fleet(self):
        """Create the fleet of aliens"""
        #Creating an alien and find the number of aliens in a row.
        #Spacing between each alien is equal to one alien width.
        #Creating an alien but not adding it o the fleet.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        #Calculating the avaliable horizontal space for the aliens.
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_alien_x = available_space_x // (2 * alien_width)
        
        #Dteremine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        
        #Create the full fleet of aliens.
        for row_number in range(number_rows):
            #Creating the first row of aliens.
            for alien_number in range(number_alien_x):
                self._create_alien(alien_number, row_number)
            
    def _create_alien(self, alien_number, row_number):
         #Creating an alien and place it in a row.
            alien = Alien(self)
            alien_width, alien_height = alien.rect.size
            alien.x = alien_width + 2 * alien_width * alien_number
            alien.rect.x =alien.x
            alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
            self.aliens.add(alien)
            
    def _check_fleet_edges(self):
        """Responds appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """Drop the entie fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
        
    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            #Decrement ship_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            
            #Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
            
            #Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()
            
            #Pause
            sleep(1.0)
        else:
            self.stats.game_active = False
        
    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                #Treat this the same as if the ship got hit
                self._ship_hit()
                break
                
    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        #Redraw the screen during each pass through the loop
        self.screen.fill(self.settings.bg_color)
        #draws the ship to the screen
        self.ship.blitme()
        #draws all fired bullets on the screen
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        #Updates screen to draw aliens on the screen
        self.aliens.draw(self.screen)
        
        #Draw the score information.
        self.sb.show_score()
        
        #Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
            
            
if __name__ == '__main__':
    #Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()