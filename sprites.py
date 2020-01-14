import pygame


#====================
pygame.mixer.init(frequency=48000, channels=6)
train_hit = pygame.mixer.Sound('sprites/sounds/train_hit.wav')
train_hit.set_volume(0.2)
bg_music = pygame.mixer.Sound('sprites/sounds/bg.wav')
bg_music.set_volume(0.2)
car_hit_sound = pygame.mixer.Sound('sprites/sounds/car_hit.wav')
car_hit_sound.set_volume(0.4)
splash = pygame.mixer.Sound('sprites/sounds/splash.wav')
splash.set_volume(0.2)
trap_hit = pygame.mixer.Sound('sprites/sounds/trap_hit.wav')
trap_hit.set_volume(0.2)
jump_sound = pygame.mixer.Sound('sprites/sounds/jump.wav')
jump_sound.set_volume(0.05)
horn = pygame.mixer.Sound('sprites/sounds/horn.wav')
horn.set_volume(0.1)
#====================
grass_block = pygame.image.load('sprites/lines/grass_block.png')
road_block = pygame.image.load('sprites/lines/road_block.png')
river_block = pygame.image.load('sprites/lines/river_block.png')
railway_block = pygame.image.load('sprites/lines/railway_block.png')
#====================
cars = [pygame.image.load(f'sprites/sprites/car{i}.png') for i in range(1, 8)]
traps = [pygame.image.load(f'sprites/sprites/trap{i}.png') for i in range(1, 4)]
tree = pygame.image.load('sprites/sprites/tree.png')
head_img = pygame.image.load('sprites\\sprites\\head_vagon.png')
mid_img = pygame.image.load('sprites\\sprites\\mid_vagon.png')
semafor = pygame.image.load('sprites/lines/semafor.png')