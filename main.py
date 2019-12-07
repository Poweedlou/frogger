from pygame import Color, Rect
import pygame.display
import pygame.image as img
import pygame.time as time
from pygame.transform import rotate


class Field:
    def __init__(self, width, height, cell_size, chicken):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.chicken = chicken
        chicken.parent = self
        self.ch_coords = [width // 2, 4]
        self.lines = []
        self.seen_lines = []
        self.playing = False
        self.cam_y = 4
        self.ch_max_y = 4
        self.max_cam_y = 4
        self.cam_y_real = 4
        self.cam_moves = False
        self.screen = pygame.display.set_mode((width * cell_size, height * cell_size))

    def play(self):
        if self.playing:
            self.lines.clear()
        self.playing = not self.playing
    
    def frame(self, force=False):
        if self.playing or force:
            y = self.ch_coords[1]
            self.cam_y_real += 0.02
            if y > self.cam_y:
                self.cam_y += (y - self.cam_y) * 0.05
            if self.cam_y_real > self.cam_y:
                self.cam_y = self.cam_y_real
            new_lines = []
            for line in self.lines:
                if line.y >= self.cam_y - 4:
                    new_lines.append(line)
            for i in range(int(self.cam_y) - 4, int(self.cam_y) - 3 + self.height):
                if i not in self.seen_lines:
                    line = self.gen_line(i)
                    new_lines.append(line)
                    self.seen_lines.append(i)
            self.lines = new_lines
            self.render()

    def move_chicken(self, dir_):
        self.ch_coords[0] += dir_[0]
        self.ch_coords[1] += dir_[1]
        if dir_[0] == 0:
            if dir_[1] > 0:
                angle = 0
            else:
                angle = 180
        elif dir_[0] > 0:
            angle = 90
        else:
            angle = 270
        self.chicken.turn(angle)
        self.playing = True
    
    def gen_line(self, y):
        bg = Color(['white', 'blue'][y % 2])
        return Line(y, self, bg)

    def render(self):
        self.screen.fill((255, 255, 255))
        for i in self.lines:
            i.render()
        self.chicken.render()


class Line:
    def __init__(self, y, parent, color):
        self.y = y
        self.color = color
        self.parent = parent
    
    def render(self):
        scr = self.parent.screen
        width = self.parent.width
        cell = self.parent.cell_size
        cam_y = self.parent.cam_y - 4
        y = (self.parent.height - self.y - 1 + cam_y) * cell
        rect_ = Rect(0, y, width * cell, cell)
        scr.fill(self.color, rect_)


class Chicken:
    def __init__(self, pic_path, ):
        self.sprite = img.load('sprites/chicken/' + pic_path + '.png')
        self.angle = 0
    
    def render(self):
        x, y = self.parent.ch_coords
        x *= self.parent.cell_size
        y = (self.parent.height - 5 - y + self.parent.cam_y) * self.parent.cell_size
        self.parent.screen.blit(self.sprite, (x, y))
    
    def turn(self, angle):
        rotate(self.sprite, angle - self.angle)
        self.angle = angle

if __name__ == "__main__":
    fps = 60
    moves = {pygame.K_w: (0, 1),
             pygame.K_s: (0, -1),
             pygame.K_a: (-1, 0),
             pygame.K_d: (1, 0)}
    chicken = Chicken('chicken')
    field = Field(11, 20, 30, chicken)
    running = True
    field.frame(True)
    clock = time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                try:
                    field.move_chicken(moves[event.key])
                except:
                    pass
        clock.tick(fps)
        field.frame()
        pygame.display.flip()
