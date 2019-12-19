from pygame import Color, Rect
import pygame
import pygame.display
import pygame.image as img
import pygame.time as time
from pygame.transform import rotate, flip


class Field:
    def __init__(self, width, height, cell_size, chicken):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.chicken = chicken
        self.ch_group = pygame.sprite.Group(chicken)
        self.ch_coords = [width // 2, 4]
        self.lines = []
        self.seen_lines = 0
        self.playing = False
        self.cam_y = 0
        self.ch_max_y = 4
        self.cam_y_real = 0
        x = width * cell_size
        y = height * cell_size
        self.screen = pygame.display.set_mode((x, y))
        self.screen2 = pygame.Surface((x, y + cell_size))
        self.screen_size = (x, y)
        chicken.add_field(self)

    def frame(self, force=False):
        if self.playing or force:
            y = self.ch_coords[1]
            self.cam_y_real += 0.02
            if y > self.cam_y + 4:
                self.cam_y += (y - self.cam_y - 4) * 0.05
            if self.cam_y_real > self.cam_y:
                self.cam_y = self.cam_y_real
            new_lines = []
            for line in self.lines:
                if line.y > self.cam_y - 1:
                    new_lines.append(line)
            upper_border = int(self.cam_y) + self.height + 1
            for i in range(self.seen_lines, upper_border):
                line = self.gen_line(i)
                new_lines.append(line)
            self.seen_lines = upper_border
            self.lines = new_lines
            self.chicken.calc()
            self.render()

    def move_chicken(self, dir_):
        self.ch_coords[0] += dir_[0]
        self.ch_coords[1] += dir_[1]
        self.chicken.hop(dir_)
    
    def gen_line(self, y):
        bg = Color(['white', 'blue'][y % 2])
        return Line(y, bg, self.width, self.cell_size)

    def render(self):
        shift = int(self.cam_y)
        lines = map(Line.render, self.lines)
        lines = map(lambda x: (x[0], (0, (x[1] - shift) * self.cell_size)), lines)
        self.screen2.blits(lines)
        ch_x, ch_y = self.ch_coords
        ch_y -= shift
        ch_x *= self.cell_size
        ch_y *= self.cell_size
        self.ch_group.draw(self.screen2)
        foo = flip(self.screen2, False, True)
        y_blit = self.cell_size * (1 - self.cam_y + shift)
        blit_area = Rect((0, y_blit), self.screen_size)
        self.screen.blit(foo, (0, 0), area=blit_area)


class Line:
    def __init__(self, y, color, width, cell_size):
        self.y = y
        size = (width * cell_size, cell_size)
        self.screen = pygame.Surface(size)
        self.screen.fill(color)
    
    def render(self):
        return self.screen, self.y


class Chicken(pygame.sprite.Sprite):
    def __init__(self, pic_path):
        super().__init__()
        self.sit_img = img.load('sprites/chicken/' + pic_path + '_sit.png')
        self.image = self.sit_img
        self.fly_img = img.load('sprites/chicken/' + pic_path + '_fly.png')
        self.rect = self.image.get_rect()
        self.angle = 0
        self.flying = False
        self.flying_frames = 0

    def fly_frame(self):
        if not self.flying:
            return
        if self.flying_frames == 14:
            self.flying_frames = 0
            self.flying = False
            self.image = rotate(self.sit_img, self.angle)
            return
        self.vx += self.dx
        self.vy += self.dy
        self.flying_frames += 1
    
    def add_field(self, field):
        self.field = field
        self.rx, self.ry = field.ch_coords
    
    def calc(self):
        cell = self.field.cell_size
        if self.flying:
            self.fly_frame()
            self.rect.x = self.vx * cell
            self.rect.y = cell * (self.vy - self.field.seen_lines + self.field.height)
        else:
            self.rect.x = self.rx * cell
            self.rect.y = cell * (self.ry - self.field.seen_lines + self.field.height)
    
    def turn(self, angle):
        self.image = rotate(self.image, angle - self.angle)
        self.angle = angle
    
    def hop(self, dir_):
        self.flying = True
        self.flying_frames = 0
        self.vx, self.vy = self.rx, self.ry
        self.dx, self.dy = dir_[0] / 15, dir_[1] / 15
        self.rx += dir_[0]
        self.ry += dir_[1]
        if dir_[0] == 0:
            if dir_[1] > 0:
                angle = 0
            else:
                angle = 180
        elif dir_[0] > 0:
            angle = 90
        else:
            angle = 270
        self.angle = angle
        self.image = rotate(self.fly_img, angle)


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
                    field.playing = True
                    field.move_chicken(moves[event.key])
                except:
                    pass
        clock.tick(fps)
        field.frame()
        pygame.display.flip()
