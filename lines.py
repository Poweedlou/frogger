import pygame


class Line:
    def __init__(self, y, color, width, cell_size):
        self.y = y
        size = (width * cell_size, cell_size)
        self.cell_size = cell_size
        self.width = width
        self.screen = pygame.Surface(size)
        self.screen.fill(color)
    
    def render(self):
        return self.screen, self.y

    def update(self):
        pass


class GrassLine(Line):
    def __init__(self, *args):
        super().__init__(*args)
        self.grass_block = pygame.image.load('sprites/lines/grass_block.png')
        for x in range(self.width):
            self.screen.blit(self.grass_block, (self.cell_size * x, 0))