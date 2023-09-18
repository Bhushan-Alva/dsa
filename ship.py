import pygame
from pygame.sprite import Sprite


class Ship(Sprite):
    """class to manage ship"""
    def __init__(self, ai_game):
        """initiate ship and set its starting position"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()

        # position ship at bottom center of screen
        self.rect.midbottom = self.screen_rect.midbottom

        # stores horizontal position of x
        self.x = float(self.rect.x)

        """movement flag"""
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """update ship's position based on movement flag"""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        self.rect.x = self.x

    def blitme(self):
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        """centers the ship on the screen"""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)
