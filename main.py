from pygame import Color, Rect
import pygame
import pygame.display
import pygame.image as img
import pygame.time as time
from pygame.transform import rotate, flip
from lines import GrassLine, RoadLine, RiverLine
from constants import *
from random import choice, randint
import sys


class Field:
    def __init__(self, chicken):
        self.chicken = chicken
        self.ch_group = pygame.sprite.Group(chicken)
        self.ch_coords = [width // 2, 4]
        self.all_group = pygame.sprite.Group()
        self.cars_group = pygame.sprite.Group()
        self.tree_group = pygame.sprite.Group()
        self.lines = []
        self.seen_lines = -height
        self.playing = False
        self.cam_y = 0
        self.ded = False
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
            self.cam_y_real += 1 / fps
            if y > self.cam_y + 4:
                self.cam_y += (y - self.cam_y - 4) * 0.05
            if self.cam_y_real > self.cam_y:
                self.cam_y = self.cam_y_real
            new_lines = []
            for line in self.lines:
                if line.y > self.cam_y - 1:
                    new_lines.append(line)
            upper_border = int(self.cam_y) + 1
            for i in range(self.seen_lines + height, upper_border + height):
                line = self.gen_line(i)
                new_lines.append(line)
                self.all_group.update(True)
                self.seen_lines += 1
            self.seen_lines = upper_border
            self.lines = new_lines
            if self.ch_coords[1] < self.seen_lines and not self.ded:
                self.u_ded()
            if self.on_tree() and not self.chicken.flying:
                x = self.ch_coords[0] + self.on_tree()[0].dx / cell_size
                y = self.ch_coords[1]
                self.ch_coords = x, y
            self.chicken.calc()
            self.all_group.update()
            if self.check_ded():
                self.u_ded()
            self.render()

    def check_ded(self):
        if pygame.sprite.spritecollide(self.chicken, self.cars_group,
                                       False, collided=pygame.sprite.collide_mask):
            return True
        if self.in_water():
            if not self.on_tree() and not self.chicken.flying:
                return True
        return False

    def u_ded(self):
        self.chicken.die_lol()
        self.ded = True # sad moment

    def move_chicken(self, dir_):
        if self.ded:
            return
        self.chicken.flying = False
        self.chicken.calc()
        adir = dir_[:]
        dx = 0
        nx = self.ch_coords[0] + dir_[0]
        if self.on_tree() and dir_[0]:
            dx = self.on_tree()[0].dx
            nx += dx / cell_size * (fps // 4 - 1)
        ny = self.ch_coords[1] + dir_[1]
        if self.in_water():
            if not self.on_tree():
                self.u_ded()
                return
        if 0 <= nx < width:
            self.ch_coords = nx, ny
            if dir_[0]:
                dir_ = dir_[0] + dx / cell_size * (fps // 4 - 1), dir_[1]
            self.chicken.hop(dir_, adir)

    def in_water(self):
        return isinstance(self.lines[self.ch_coords[1] - self.seen_lines], RiverLine)

    def on_tree(self):
        a = pygame.sprite.spritecollide(self.chicken, self.tree_group,
                                        False, collided=pygame.sprite.collide_mask)
        return a

    def gen_line(self, y):
        if -self.seen_lines > height - 5:
            return GrassLine(y,self)
        Foo = choice((GrassLine, RoadLine, RiverLine))
        if Foo in (RoadLine, RiverLine):
            speed = choice((randint(1, 4), randint(-4, -1))) / 6
            if speed < 0:
                speed -= 1
            else:
                speed += 1
            return Foo(y, self, dx=speed)
        else:
            return Foo(y, self)

    def render(self):
        shift = int(self.cam_y)
        lines = map(lambda x: x.render(), self.lines)
        lines = map(lambda x: (x[0], (0, (x[1] - shift) * cell_size)), lines)
        self.screen2.blits(lines)
        self.all_group.draw(self.screen2)
        self.ch_group.draw(self.screen2)
        foo = flip(self.screen2, False, True)
        y_blit = cell_size * (1 - self.cam_y + shift)
        blit_area = Rect((0, y_blit), self.screen_size)
        self.screen.blit(foo, (0, 0), area=blit_area)


class Chicken(pygame.sprite.Sprite):
    def __init__(self, pic_path):
        super().__init__()
        self.sit_img = img.load('sprites/chicken/' + pic_path + '_sit.png')
        self.image = self.sit_img
        self.fly_img = img.load('sprites/chicken/' + pic_path + '_fly.png')
        self.tomb_img = img.load('sprites/tomb.png')
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.angle = 0
        self.flying = False
        self.flying_frames = 0

    def fly_frame(self):
        if not self.flying:
            return
        if self.flying_frames == fps // 4 - 1:
            self.flying_frames = 0
            self.flying = False
            self.image = rotate(self.sit_img, self.angle)
            self.mask = pygame.mask.from_surface(self.image)
            return
        self.vx += self.dx
        self.vy += self.dy
        self.flying_frames += 1

    def add_field(self, field):
        self.field = field
        self.rx, self.ry = self.field.ch_coords

    def die_lol(self):
        self.image = self.tomb_img
        self.flying = False

    def calc(self):
        if self.flying:
            self.fly_frame()
            self.rect.x = self.vx * cell_size
            self.rect.y = cell_size * (self.vy - self.field.seen_lines)
        else:
            self.rx, self.ry = self.field.ch_coords
            self.rect.x = self.rx * cell_size
            self.rect.y = cell_size * (self.ry - self.field.seen_lines)

    def turn(self, angle):
        self.image = rotate(self.image, angle - self.angle)
        self.angle = angle

    def hop(self, dir_, angle_dir):
        self.flying = True
        self.flying_frames = 0
        self.vx, self.vy = self.rx, self.ry
        self.dx, self.dy = dir_[0] * 4 / fps, dir_[1] * 4 / fps
        self.rx += dir_[0]
        self.ry += dir_[1]
        if angle_dir[0] == 0:
            if angle_dir[1] > 0:
                angle = 0
            else:
                angle = 180
        elif angle_dir[0] > 0:
            angle = 90
        else:
            angle = 270
        self.angle = angle
        self.image = rotate(self.fly_img, angle)
        self.mask = pygame.mask.from_surface(self.image)


if __name__ == "__main__":
    moves = {pygame.K_w: (0, 1),
             pygame.K_s: (0, -1),
             pygame.K_a: (-1, 0),
             pygame.K_d: (1, 0)}
    chicken = Chicken('chicken')
    field = Field(chicken)
    running = True
    field.frame(True)
    clock = time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                try:
                    field.playing = True
                    field.move_chicken(moves[event.key])
                except:
                    pass
        bar = 1000 / clock.tick(fps)
        #print(bar)
        field.frame()
        pygame.display.flip()
