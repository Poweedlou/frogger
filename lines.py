import pygame
from random import choice
from constants import *


class Line:
    def __init__(self, y, field):
        self.y = y
        self.field = field
        size = (width * cell_size, cell_size)
        self.screen = pygame.Surface(size)
        self.screen.fill(pygame.Color('white'))
    
    def render(self):
        return self.screen, self.y

    def update(self):
        pass


class GrassLine(Line):
    def __init__(self, *args):
        super().__init__(*args)
        self.block = pygame.image.load('sprites/lines/grass_block.png')
        for x in range(width):
            self.screen.blit(self.block, (cell_size * x, 0))


class RoadLine(Line):
    def __init__(self, *args, dx=1):
        super().__init__(*args)
        self.block = pygame.image.load('sprites/lines/road_block.png')
        self.cars = []
        for x in range(width):
            self.screen.blit(self.block, (cell_size * x, 0))
        self.dx = dx
        for i in range(width // 4):
            x = choice(range(4)) + i * 4
            self.add_car(x)

    def add_car(self, x):
        g1 = self.field.cars_group
        g2 = self.field.all_group
        car = Car(self.y - self.field.seen_lines + 1, x, self.dx)
        car.add(g1, g2)
        self.cars.append(car)

class Car(pygame.sprite.Sprite):
    def __init__(self, y, x, dx):
        super().__init__()
        num = choice('1234567')
        self.image = pygame.image.load(f'sprites/sprites/car{num}.png')
        self.mask = pygame.mask.from_surface(self.image)
        if dx > 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.y = y
        self.dy = choice((-1, 1))
        self.dx = dx
        self.x = x * cell_size
        
    def update(self, y_shift=False):
        if y_shift:
            self.y -= 1
            if self.y < 0:
                self.kill()
            return
        self.x += self.dx
        if self.dx > 0:
            if self.x > width * cell_size:
                self.x = -cell_size
        elif self.x <= 0:
            self.x = (width + 1) * cell_size
        self.rect.y = self.y * cell_size
        self.rect.y += self.dy
        self.dy = -self.dy
        self.rect.x = int(self.x)