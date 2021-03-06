from pygame import Color, Rect
import pygame
import pygame.display
import pygame.image as img
import pygame.time as time
from pygame.transform import rotate, flip  # pygame для отрисовки итд
from lines import (GrassLine, RoadLine, RiverLine,
                   TrainLine, TrapLine, Particle)  # Мои классы линий
from constants import *  # Константы игрового поля
from random import choice, randint, random
from math import sin, pi  # математика
import sys
from stats import add_score  # изменяет файл с очками


train_hit = pygame.mixer.Sound('sprites/sounds/train_hit.wav')
train_hit.set_volume(0.2)
bg_music = pygame.mixer.Sound('sprites/sounds/bg.wav')
bg_music.set_volume(0.2)
car_hit_sound = pygame.mixer.Sound('sprites/sounds/car_hit.wav')
car_hit_sound.set_volume(0.4)
splash = pygame.mixer.Sound('sprites/sounds/splash.wav')
splash.set_volume(0.2)
trap_hit = pygame.mixer.Sound('sprites/sounds/trap_hit.wav')
trap_hit.set_volume(0.4)
jump_sound = pygame.mixer.Sound('sprites/sounds/jump.wav')
jump_sound.set_volume(0.05)
# звуки и спрайты вынесены отдельно


pygame.font.init()
bg_music.set_volume(0.1)
bg_music.play(loops=-1)
pygame.mixer.set_reserved(1)
# фоновая музыка


class Field:
    '''Класс поля'''
    def __init__(self, chicken):
        self.chicken = chicken
        self.line_plan = (5, GrassLine)
        self.ch_group = pygame.sprite.Group(chicken)
        self.ch_coords = [width // 2 + 1, 4]

        self.all_group = pygame.sprite.Group()
        self.cars_group = pygame.sprite.Group()
        self.trap_group = pygame.sprite.Group()
        self.tree_group = pygame.sprite.Group()
        self.train_group = pygame.sprite.Group()
        # группы для проверки столкновений

        self.train_lines = []
        self.lines = []
        self.seen_lines = -height
        self.playing = False
        self.cam_y = 0
        self.ded = False
        self.ch_max_y = 4
        self.cam_y_real = 0
        x = width * cell_size
        y = height * cell_size
        self.screen = pygame.display.set_mode((x - 3 * cell_size, y))
        # экран посредник
        self.screen2 = pygame.Surface((x, y + cell_size))
        self.screen_size = (x - 3 * cell_size, y)
        chicken.add_field(self)

    def frame(self, force=False):
        '''Основной цикл событий. Двигает камеру и создаёт новые линии'''
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
                elif line in self.train_lines:
                    self.train_lines.pop(self.train_lines.index(line))
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
            if self.on_tree() and not self.chicken.flying and not self.ded:
                x = self.ch_coords[0] + self.on_tree()[0].dx / cell_size
                y = self.ch_coords[1]
                self.ch_coords = x, y
            for tl in self.train_lines:
                tl.frame()
            self.chicken.calc()
            self.all_group.update()
            self.check_ded()
            y = int(self.ch_coords[1])
            if y > self.ch_max_y:
                self.ch_max_y = y
            self.render()

    def check_ded(self):
        '''Проверяет, жива ли курица в её текущем положении,
        проигрывает звуки столкновений'''
        if self.ded:
            return
        a = pygame.sprite.spritecollide(self.chicken, self.cars_group,
                                        False,
                                        collided=pygame.sprite.collide_mask)
        if a:
            self.u_ded(a[0].dx)
            car_hit_sound.play()
        if self.in_water():
            if not self.on_tree() and not self.chicken.flying:
                self.u_ded()
                splash.play()
        if not (2.1 < self.chicken.rect.x / cell_size < width - 0.1):
            self.u_ded()
        a = pygame.sprite.spritecollide(self.chicken, self.train_group,
                                        False,
                                        collided=pygame.sprite.collide_mask)
        if a:
            train_hit.play()
            self.u_ded(a[0].dx / 2)
        a = pygame.sprite.spritecollide(self.chicken, self.trap_group,
                                        False,
                                        collided=pygame.sprite.collide_mask)
        if a:
            self.u_ded()
            a[0].catch()
            trap_hit.play()

    def u_ded(self, dir_=1):
        '''Убивает курицу'''
        jump_sound.stop()
        self.chicken.die_lol(dir_)
        self.ded = True  # sad moment

    def move_chicken(self, dir_):
        '''Заставляет курицу прыгать, учитывает движение брёвен на реке'''
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
                splash.play()
                self.u_ded()
                return
        self.ch_coords = nx, ny
        if dir_[0]:
            dir_ = dir_[0] + dx / cell_size * (fps // 4 - 1), dir_[1]
        self.chicken.hop(dir_, adir)

    def in_water(self):
        '''Проверяет, находится ли курица над водой'''
        return isinstance(self.lines[self.ch_coords[1] - self.seen_lines],
                          RiverLine)

    def on_tree(self):
        '''Проверяет, стоит ли курица на бревне'''
        a = pygame.sprite.spritecollide(self.chicken, self.tree_group,
                                        False,
                                        collided=pygame.sprite.collide_mask)
        return a

    def gen_line(self, y):
        '''Генерирует линии в соответствии с планом'''
        Foo = self.line_plan[1]
        if self.line_plan[0] == 1:
            ch = set((GrassLine, RoadLine, RiverLine, TrainLine, TrapLine))
            ch.discard(Foo)
            Bar = choice(list(ch))
            if Bar in (TrainLine, TrapLine):
                len_ = 1
            elif Bar == GrassLine:
                len_ = randint(1, 2)
            else:
                len_ = randint(2, 3)
            self.line_plan = len_, Bar
        else:
            self.line_plan = self.line_plan[0] - 1, Foo
        if Foo in (RoadLine, RiverLine):
            speed = choice((randint(1, 4), randint(-4, -1))) / 6
            if speed < 0:
                speed -= 1
            else:
                speed += 1
            return Foo(y, self, dx=speed)
        elif Foo == TrainLine:
            speed = choice((-30, 30))
            line = Foo(y, self, dx=speed)
            self.train_lines.append(line)
            return line
        else:
            return Foo(y, self)

    def render(self):
        '''Отрисовывает всё на экране'''
        shift = int(self.cam_y)
        lines = map(lambda x: x.render(), self.lines)
        lines = map(lambda x: (x[0], (0, (x[1] - shift) * cell_size)), lines)
        self.screen2.blits(lines)
        self.all_group.draw(self.screen2)
        self.ch_group.draw(self.screen2)
        foo = flip(self.screen2, False, True)
        y_blit = cell_size * (1 - self.cam_y + shift)
        blit_area = Rect((3 * cell_size, int(y_blit)), self.screen_size)
        self.screen.blit(foo, (0, 0), area=blit_area)
        self.print_score()

    def print_fps(self, fps):
        '''Печатает реальный фпс'''
        font = pygame.font.Font(None, 50)
        text = font.render(str(int(fps)), 1, (37, 40, 80))
        self.screen.blit(text, ((width - 4) * cell_size, 0))

    def print_score(self):
        '''Печатает кол-во очков'''
        font = pygame.font.Font(None, 50)
        text = font.render(str(self.ch_max_y), 1, (37, 40, 80))
        self.screen.blit(text, ((width // 2 - 1) * cell_size, 0))

    def add_particles(self, coords):
        '''Создаёт много частиц. Вызывается после смерти'''
        for i in range(20):
            dx = random() * 4 - 2
            ddx = 0.95
            ddy = 0.99
            ttl = (random() + 1) * fps
            dy = random() + 1
            particle = Particle(coords, dx, dy, ddx, ddy, ttl)
            self.all_group.add(particle)


class Chicken(pygame.sprite.Sprite):
    '''Главный герой игры'''
    def __init__(self, pic_path):
        super().__init__()
        self.ded = 0
        self.dedtime = 0
        self.sit_img = img.load('sprites/chicken/' + pic_path + '_sit.png')
        self.image = self.sit_img
        self.fly_img = img.load('sprites/chicken/' + pic_path + '_fly.png')
        self.tomb_img = img.load('sprites/chicken/tomb.png')
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.angle = 0
        self.flying = False
        self.flying_frames = 0

    def fly_frame(self):
        '''Обновляет положение во время прыжка'''
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
        '''Привязывает поле к курице'''
        self.field = field
        self.rx, self.ry = self.field.ch_coords

    def die_lol(self, dir_=1):
        '''Убивает курицу, меняет картинку'''
        if not self.ded:
            c = (self.rx * cell_size + cell_size // 2,
                 (self.ry - self.field.seen_lines) *
                 cell_size + cell_size // 2)
            self.field.add_particles(c)
            add_score(self.field.ch_max_y, name)
            self.image = self.tomb_img
            self.flying = False
            self.ded = dir_

    def calc(self):
        '''Рассчитывает положение курицы'''
        if self.ded:
            if self.dedtime == 0:
                self.ded_pos_y = self.ry
                self.vy = self.ry
                self.vx = self.rx
            if self.dedtime < fps / 2:
                self.dedtime += 1
                self.vx += self.ded * 1.5 / cell_size
                self.vy = self.ded_pos_y + sin(self.dedtime *
                                               pi * 2 / fps) / 1.5
            self.rect.x = int(self.vx * cell_size)
            self.rect.y = int(cell_size * (self.vy - self.field.seen_lines))
            return
        if self.flying:
            self.fly_frame()
            self.rect.x = int(self.vx * cell_size)
            self.rect.y = int(cell_size * (self.vy - self.field.seen_lines))
        else:
            self.rx, self.ry = self.field.ch_coords
            self.rect.x = int(self.rx * cell_size)
            self.rect.y = int(cell_size * (self.ry - self.field.seen_lines))

    def turn(self, angle):
        '''Поворачивает курицу'''
        self.image = rotate(self.image, angle - self.angle)
        self.angle = angle

    def hop(self, dir_, angle_dir):
        '''Заставляет курицу прыгать'''
        jump_sound.play()
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


def game_pack(ch_name):
    '''Создаёт курицу и поле'''
    chicken = Chicken(ch_name)
    field = Field(chicken)
    field.frame(True)
    return chicken, field


def draw_FROGGER(field):
    '''Рисует надпись frogger на экране'''
    w, h = field.screen_size
    x = w // 4
    y = h // 4
    font = pygame.font.SysFont('comicsansms', 100, True)
    text = font.render('Frogger', 1, (255, 0, 200))
    field.screen.blit(text, (x, y))


if __name__ == "__main__":
    name = input('Введите имя\n')
    moves = {pygame.K_w: (0, 1),
             pygame.K_s: (0, -1),
             pygame.K_a: (-1, 0),
             pygame.K_d: (1, 0),
             pygame.K_UP: (0, 1),
             pygame.K_DOWN: (0, -1),
             pygame.K_LEFT: (-1, 0),
             pygame.K_RIGHT: (1, 0)}
    running = True
    chicken, field = game_pack("chicken")
    clock = time.Clock()
    draw_FROGGER(field)
    '''Главный цикл программы'''
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    del chicken
                    del field
                    chicken, field = game_pack("chicken")
                else:
                    try:
                        field.playing = True
                        field.move_chicken(moves[event.key])
                    except:
                        field.playing = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and field.playing:
                    x, y = event.pos
                    y = (height + (field.cam_y -
                                   int(field.cam_y))) * cell_size - y
                    x += 3 * cell_size
                    field.add_particles((x, y))
        bar = 1000 / clock.tick(fps)
        field.frame()
        if field.playing:
            field.print_fps(bar)
        pygame.display.flip()
