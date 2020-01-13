import pygame
from random import choice, randint
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
        for x in range(width):
            self.screen.blit(self.block, (cell_size * x, 0))
        self.dx = dx
        for i in range(width // 4):
            x = choice(range(3)) + i * 4
            self.add_car(x)

    def add_car(self, x):
        g1 = self.field.cars_group
        g2 = self.field.all_group
        car = Car(self.y - self.field.seen_lines + 1, x, self.dx)
        car.add(g1, g2)

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


class RiverLine(Line):
    def __init__(self, *args, dx=1):
        super().__init__(*args)
        self.block = pygame.image.load('sprites/lines/river_block.png')
        self.dx = dx
        for x in range(width):
            self.screen.blit(self.block, (cell_size * x, 0))
        for i in range(width // 5):
            x = choice(range(2)) + i * 5
            self.add_tree(x)
    
    def add_tree(self, x):
        g1 = self.field.tree_group
        g2 = self.field.all_group
        tree = Tree(self.y - self.field.seen_lines + 1, x, self.dx)
        tree.add(g1, g2)


class Tree(pygame.sprite.Sprite):
    def __init__(self, y, x, dx):
        super().__init__()
        self.image = pygame.image.load('sprites/sprites/tree.png')
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.y = y
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
        self.rect.x = int(self.x)


class TrainLine(Line):
    def __init__(self, *args, dx=10):
        super().__init__(*args)
        self.block = pygame.image.load('sprites/lines/railway_block.png')
        for x in range(width):
            self.screen.blit(self.block, (cell_size * x, 0))
        self.dx = dx
        self.train_exists = False
        self.ttl = choice(range(2, 5)) * fps
        self.draw_semafor('green')

    def draw_semafor(self, color):
        self.screen.blit(pygame.image.load('sprites/lines/semafor.png'), (3 * cell_size, 0))
        pygame.draw.circle(self.screen, pygame.Color(color),
                           (3 * cell_size + 10, 31),
                           cell_size // 8)

    def frame(self):
        if not self.train_exists:
            self.ttl -= 1
            if self.ttl < fps and not self.ttl % (fps // 5):
                if self.ttl // (fps // 5) % 2:
                    self.draw_semafor('white')
                else:
                    self.draw_semafor('red')
            elif self.ttl >= fps:
                self.draw_semafor('green')
            if not self.ttl:
                self.add_train()
                self.ttl = choice(range(2, 5)) * fps

    def add_train(self):
        g1 = self.field.train_group
        g2 = self.field.all_group
        train = Train(self.dx, self.y - self.field.seen_lines + 1, self)
        s = pygame.mixer.Sound('sprites/sounds/horn.wav')
        s.set_volume(0.2)
        s.play()
        for vagon in train.train_arr:
            vagon.add(g1, g2)
        self.train = train
        self.train_exists = True


class Vagon(pygame.sprite.Sprite):
    def __init__(self, dx, img, x, y):
        super().__init__()
        self.line = None
        self.image = img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.y = y * cell_size
        self.y = y
        self.dx = dx
        self.x = x * cell_size

    def update(self, y_shift=False):
        if y_shift:
            self.y -= 1
            if self.y < 0:
                self.kill()
            else:
                self.rect.y -= cell_size
            return
        self.x += self.dx
        self.rect.x = int(self.x)
        if self.dx > 0:
            if self.rect.x >= width * cell_size:
                self.kill()
                if self.line is not None:
                    self.line.train_exists = False
                    self.line.train = None
        elif self.rect.x <= 0:
            self.kill()
            if self.line is not None:
                self.line.train_exists = False
                self.line.train = None


class Train:
    def __init__(self, dx, y, line):
        self.line = line
        self.dx = dx
        head_img = pygame.image.load('sprites\\sprites\\head_vagon.png')
        mid_img = pygame.image.load('sprites\\sprites\\mid_vagon.png')
        if dx < 0:
            x_cs = list(range(width, width + 10, 3))
        else:
            x_cs = list(range(-9, 1, 3))
        p1 = Vagon(dx, head_img, x_cs[0], y)
        p2 = Vagon(dx, mid_img, x_cs[1], y)
        p3 = Vagon(dx, mid_img, x_cs[2], y)
        p4 = Vagon(dx, pygame.transform.flip(head_img, True, False), x_cs[3], y)
        if dx < 0:
            p4.line = line
        else:
            p1.line = line
        self.train_arr = (p1, p2, p3, p4)


class TrapLine(Line):
    def __init__(self, *args):
        super().__init__(*args)
        self.block = pygame.image.load('sprites/lines/grass_block.png')
        for x in range(width):
            self.screen.blit(self.block, (cell_size * x, 0))
        g1 = self.field.all_group
        g2 = self.field.trap_group
        for x in range(3, width - 3, 4):
            dx = randint(-2, 2)
            trap = Trap(x + 2 + dx, self.y - self.field.seen_lines + 1)
            trap.add(g1, g2)


class Trap(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('sprites/sprites/trap1.png')
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.y = y * cell_size
        self.rect.x = x * cell_size
        self.caught = -1
    
    def update(self, y_shift=False):
        if y_shift:
            self.rect.y -= cell_size
            if self.rect.y < 0:
                self.kill()
        if self.caught > 0:
            self.caught = self.caught - 1
        elif not self.caught:
            self.caught = -1
            self.image = pygame.image.load('sprites/sprites/trap3.png')
        
    
    def catch(self):
        self.caught = fps // 10
        self.image = pygame.image.load('sprites/sprites/trap2.png')