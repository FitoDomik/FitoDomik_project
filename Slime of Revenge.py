import pygame
import math
import sys
import ast
import os
from win32api import GetSystemMetrics
from enum import Enum
import json
import random
pygame.font.init()
lol = os.path.dirname(os.path.abspath(__file__))
def load_settings():
    default_settings = {
        "fullscreen": False,
        "keys": {
            "UP": pygame.K_w,
            "DOWN": pygame.K_s,
            "LEFT": pygame.K_a,
            "RIGHT": pygame.K_d,
            "JUMP": pygame.K_SPACE,
            "DASH": pygame.K_RSHIFT,
            "SHOOT": "MOUSE_1"
        },
        "sound": {
            "music_volume": 15,
            "sfx_volume": 100
        },
        "display": {
            "show_fps": True,
            "parallax_background": True,
            "background_type": "night"
        },
        "statistics": {
            "level_times": {},
            "level_deaths": {},
            "current_level_start_time": 0,
            "current_level_deaths": 0,
            "current_level_name": ""
        }
    }
    try:
        with open('settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
            for key in default_settings:
                if key not in settings:
                    settings[key] = default_settings[key]
                elif isinstance(default_settings[key], dict):
                    for subkey in default_settings[key]:
                        if subkey not in settings[key]:
                            settings[key][subkey] = default_settings[key][subkey]
            return settings
    except (FileNotFoundError, json.JSONDecodeError):
        return default_settings
def save_settings(settings):
    try:
        with open('settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка сохранения настроек: {e}")
def get_key_name(key):
    key_names = {
        pygame.K_w: "W", pygame.K_s: "S", pygame.K_a: "A", pygame.K_d: "D",
        pygame.K_SPACE: "SPACE", pygame.K_RSHIFT: "RSHIFT", pygame.K_LSHIFT: "LSHIFT",
        pygame.K_RETURN: "ENTER", pygame.K_ESCAPE: "ESC", pygame.K_TAB: "TAB",
        pygame.K_BACKSPACE: "BACKSPACE", pygame.K_DELETE: "DELETE",
        pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT", pygame.K_UP: "UP", pygame.K_DOWN: "DOWN",
        pygame.K_LCTRL: "LCTRL", pygame.K_RCTRL: "RCTRL", pygame.K_LALT: "LALT", pygame.K_RALT: "RALT",
        pygame.K_q: "Q", pygame.K_e: "E", pygame.K_r: "R", pygame.K_t: "T", pygame.K_y: "Y",
        pygame.K_u: "U", pygame.K_i: "I", pygame.K_o: "O", pygame.K_p: "P", pygame.K_f: "F",
        pygame.K_g: "G", pygame.K_h: "H", pygame.K_j: "J", pygame.K_k: "K", pygame.K_l: "L",
        pygame.K_z: "Z", pygame.K_x: "X", pygame.K_c: "C", pygame.K_v: "V", pygame.K_b: "B",
        pygame.K_n: "N", pygame.K_m: "M", pygame.K_1: "1", pygame.K_2: "2", pygame.K_3: "3",
        pygame.K_4: "4", pygame.K_5: "5", pygame.K_6: "6", pygame.K_7: "7", pygame.K_8: "8",
        pygame.K_9: "9", pygame.K_0: "0", pygame.K_BACKQUOTE: "`"
    }
    mouse_names = {
        "MOUSE_1": "ЛКМ",
        "MOUSE_2": "СКМ",
        "MOUSE_3": "ПКМ",
        "MOUSE_4": "МЫШЬ_4",
        "MOUSE_5": "МЫШЬ_5"
    }
    if isinstance(key, str) and key.startswith("MOUSE_"):
        return mouse_names.get(key, key)
    return key_names.get(key, f"KEY_{key}")
settings = load_settings()
UP = None
DOWN = None
LEFT = None
RIGHT = None
JUMP = None
DASH = None
SHOOT = None
def is_key_pressed(key_bind, event):
    if isinstance(key_bind, str) and key_bind.startswith("MOUSE_"):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_button = int(key_bind.split("_")[1])
            return event.button == mouse_button
        return False
    else:
        if event.type == pygame.KEYDOWN:
            return event.key == key_bind
        return False
def is_key_released(key_bind, event):
    if isinstance(key_bind, str) and key_bind.startswith("MOUSE_"):
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_button = int(key_bind.split("_")[1])
            return event.button == mouse_button
        return False
    else:
        if event.type == pygame.KEYUP:
            return event.key == key_bind
        return False
def init_keys():
    global UP, DOWN, LEFT, RIGHT, JUMP, DASH, SHOOT
    UP = settings["keys"]["UP"]
    DOWN = settings["keys"]["DOWN"]
    LEFT = settings["keys"]["LEFT"]
    RIGHT = settings["keys"]["RIGHT"]
    JUMP = settings["keys"]["JUMP"]
    DASH = settings["keys"]["DASH"]
    SHOOT = settings["keys"]["SHOOT"]
init_keys()
gameButton = ""
waitingForKey = False
selectedKeyAction = ""
dragging_slider = False
dragging_type = ""
notification_text = ""
notification_time = 0
notification_duration = 3000
def update_sound_volumes():
    pygame.mixer.music.set_volume(settings["sound"]["music_volume"] / 100.0)
    sfx_vol = settings["sound"]["sfx_volume"] / 100.0
    clickSound.set_volume(1 * sfx_vol)
    scrollSound.set_volume(3 * sfx_vol)
    runSound.set_volume(0.2 * sfx_vol)
    jumpSound.set_volume(1 * sfx_vol)
    dropSound.set_volume(0.8 * sfx_vol)
    dashSound.set_volume(0.5 * sfx_vol)
    saveSound.set_volume(0.2 * sfx_vol)
    rollbackSound.set_volume(3 * sfx_vol)
    dieSound.set_volume(1 * sfx_vol)
    shootSound.set_volume(0.3 * sfx_vol)
    misfireSound.set_volume(0.7 * sfx_vol)
    chargerSound.set_volume(2 * sfx_vol)
    stopEnemyFlySound.set_volume(0.5 * sfx_vol)
    startEnemyFlySound.set_volume(4 * sfx_vol)
def start_level_timer(level_name):
    settings["statistics"]["current_level_name"] = level_name
    settings["statistics"]["current_level_start_time"] = pygame.time.get_ticks()
    settings["statistics"]["current_level_deaths"] = 0
    save_settings(settings)
def pause_on():
    settings["statistics"]["current_level_pause_on"] = pygame.time.get_ticks()
    save_settings(settings)
def pause_off():
    settings["statistics"]["current_level_start_time"] += pygame.time.get_ticks() - settings["statistics"]["current_level_pause_on"]
    save_settings(settings)
def add_death():
    if settings["statistics"]["current_level_name"]:
        settings["statistics"]["current_level_deaths"] += 1
        save_settings(settings)
def finish_level():
    if settings["statistics"]["current_level_name"]:
        level_name = settings["statistics"]["current_level_name"]
        current_time = pygame.time.get_ticks()
        level_time = (current_time - settings["statistics"]["current_level_start_time"]) / 1000.0
        is_new_record = False
        if level_name not in settings["statistics"]["level_times"] or level_time < settings["statistics"]["level_times"][level_name]:
            settings["statistics"]["level_times"][level_name] = level_time
            is_new_record = True
        settings["statistics"]["level_deaths"][level_name] = settings["statistics"]["current_level_deaths"]
        save_settings(settings)
        return [is_new_record, level_time]
def get_current_level_time():
    if settings["statistics"]["current_level_start_time"] > 0:
        current_time = pygame.time.get_ticks()
        return (current_time - settings["statistics"]["current_level_start_time"]) / 1000.0
    return 0
def format_time(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 100)
    return f"{minutes:02d}:{secs:02d}.{millisecs:02d}"
def show_notification(text):
    global notification_text, notification_time
    notification_text = text
    notification_time = pygame.time.get_ticks()
WIDTH = 889
HEIGHT = 500
BLACK = (0, 0, 0)
BLUE = (71, 153, 192)
WHITE = (225, 225, 225)
GREEN = (0, 250, 0)
GREEN2 = (150, 220, 150)
GREEN_d = (0, 255, 221)
GREEN_d2 = (151, 204, 190)
PURPLE = (171, 100, 237)
PURPLE2 = (192, 181, 196)
colorGG = GREEN
colorGG2 = GREEN2
menuColor = (33, 57, 94)
colorBullets1 = (116, 247, 40)
colorBullets2 = (60, 120, 135)
colorBullets = colorBullets2
backRED = (163, 95, 95)
backGREEN = (54, 64, 40)
backGRAY = (158, 158, 158)
backBROWN = (115, 91, 76)
backYELLOW = (184, 183, 141)
backPURPLE = (196, 183, 201)
backColor = [backRED, backGREEN, backGRAY, backBROWN, backYELLOW, backPURPLE]
createColor = backColor[0]
font = pygame.font.SysFont("Calibri", 23, 1)
menuFont = pygame.font.SysFont("Calibri", 33, 1)
fontMENU = pygame.font.SysFont("Calibri", 50, 1)
minY = HEIGHT-50
TrueX = WIDTH//2
TrueY = HEIGHT//2
x = TrueX
y = TrueY
spawnX = x
spawnY = y
xO = x
yO = y
surfX = 0
surfY = 0
spawnSX = surfX
spawnSY = surfY
mouseX = 0
mouseY = 0
firstMouseX = 0
firstMouseY = 0
map = {"block": [[], [], [], []], "spikes": [[], [], [], []], "spring": [[], [], [], []],
        "rollback": [[], [], 8, 8, []], "background": [[], [], [], [], []],
        "spawnpoint": [[], [], 21, 21, -1], "bullets": [[], [], 15, 15, [], []],
       "enemyFly": [[], [], 21, 21, [], [], [], [[], [], [], []], [], [], []], "finish": [[], [], 24, 24]}
'''
with open('map.txt', 'r') as file:
    text = file.read()
map = ast.literal_eval(text)
'''
letMap = "none"
createType = "block"
correctObject = {"block": [], "spikes": [], "spring": [], "rollback": [], "background": [],
                 "spawnpoint": [], "bullets": [], "enemyFly": [], "finish": []}
draw = 0
Size = 21
surf = 34
bullets = 0
bulletsMax = 16
inventory = [20, HEIGHT-80]
bulletsCadr = bullets * 2
bulletTime = 0
flyBullets = [[], [], [], []]
speedBullets = 30
lengthBullets = 20
motionU = "stop"
motionD = "stop"
motionL = "stop"
motionR = "stop"
jump = "stop"
jumpWallL = "stop"
jumpWallR = "stop"
dash = "stop"
shoot = "stop"
lastButton = "right"
NDash = lastButton
kG = 0.81
maxSpeed = 4
speed = 0
J = 10 * math.sqrt(kG)
SpringJ = 15 * math.sqrt(kG)
speedJ = J
maxSpeedG = 10
speedG = 0
speedSX = 0
speedSY = 0
speedDash = 10
g = 0.5 * kG
surfG = 0.4
grav = 1
canJump = False
canJumpWallL = False
canJumpWallR = False
canDash = False
canShoot = True
gameMode = "surv"
stopRun = 0
spring = 0
maxTimeDash = 15
timeDash = 0
timeShoot = 0
timeRollback = 600
timeCoyoteL = 5
timeCoyoteR = 5
menu = "menu"
buttonMenu = ["Играть", "Карты", "Создать", "Настройки", "Выйти"]
canCreate = False
'''UP = pygame.K_w
DOWN = pygame.K_s
LEFT = pygame.K_a
RIGHT = pygame.K_d
JUMP = pygame.K_SPACE
DASH = 3 
SHOOT = 1'''
gameButton = ""
FPS = 60
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
screen = pygame.Surface((WIDTH, HEIGHT))
fullScreen = True
current_size = (GetSystemMetrics(0), GetSystemMetrics(1))
def set_display_mode(enable_fullscreen):
    global fullScreen, current_size, screen0, k_posX, k_posY
    if enable_fullscreen:
        current_size = (GetSystemMetrics(0), GetSystemMetrics(1))
        screen0 = pygame.display.set_mode(current_size, pygame.FULLSCREEN)
        fullScreen = True
    else:
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        current_size = (WIDTH, HEIGHT)
        screen0 = pygame.display.set_mode(current_size, pygame.RESIZABLE)
        fullScreen = False
    k_posX = WIDTH / current_size[0]
    k_posY = HEIGHT / current_size[1]
set_display_mode(True)
star_layers = []
bg_width = WIDTH * 4
bg_height = HEIGHT * 3
moon_surface = None
moon_base_pos = (int(WIDTH * 1.6), int(HEIGHT * 0.55))
def init_parallax_background():
    global star_layers, moon_surface
    random.seed(42)
    star_layers.clear()
    layer_specs = [
        (220, 0.15, (220, 220, 255), 1),
        (140, 0.35, (200, 205, 255), 1),
        (80,  0.6,  (255, 255, 255), 2),
    ]
    for num_stars, factor, color, size in layer_specs:
        positions = [(random.randrange(0, bg_width), random.randrange(0, bg_height)) for _ in range(num_stars)]
        star_layers.append({
            "positions": positions,
            "factor": factor,
            "color": color,
            "size": size,
        })
    radius = max(40, HEIGHT // 8)
    moon_diameter = radius * 2
    surf = pygame.Surface((moon_diameter + 20, moon_diameter + 20), pygame.SRCALPHA)
    center = (surf.get_width() // 2, surf.get_height() // 2)
    for r, alpha in ((radius + 18, 20), (radius + 12, 35), (radius + 6, 60)):
        pygame.draw.circle(surf, (250, 250, 220, alpha), center, r)
    pygame.draw.circle(surf, (235, 235, 210), center, radius)
    crater_specs = [
        (-radius // 3, -radius // 4, radius // 6),
        (radius // 5, -radius // 6, radius // 7),
        (-radius // 6, radius // 6, radius // 8),
        (radius // 4, radius // 5, radius // 9),
    ]
    for dx, dy, cr in crater_specs:
        pygame.draw.circle(surf, (210, 210, 195), (center[0] + dx, center[1] + dy), cr)
        pygame.draw.circle(surf, (200, 200, 185), (center[0] + dx + cr // 4, center[1] + dy + cr // 4), cr // 2)
    global moon_surface
    moon_surface = surf
def draw_parallax_background(target_surf: pygame.Surface, camera_x: int, camera_y: int):
    target_surf.fill((6, 9, 22))
    for layer in star_layers:
        positions = layer["positions"]
        factor = layer["factor"]
        color = layer["color"]
        size = layer["size"]
        off_x = int((camera_x * factor) % bg_width)
        off_y = int((camera_y * factor) % bg_height)
        for sx, sy in positions:
            x = sx - off_x
            y = sy - off_y
            for dx in (-bg_width, 0, bg_width):
                px = x + dx
                if px < -size or px > WIDTH:
                    continue
                for dy in (-bg_height, 0, bg_height):
                    py = y + dy
                    if py < -size or py > HEIGHT:
                        continue
                    target_surf.fill(color, (px, py, size, size))
    if moon_surface is not None:
        moon_factor = 0.08
        mx = int(moon_base_pos[0] - camera_x * moon_factor)
        my = int(moon_base_pos[1] - camera_y * moon_factor)
        target_surf.blit(moon_surface, (mx - moon_surface.get_width() // 2, my - moon_surface.get_height() // 2))
init_parallax_background()
pygame.mixer.music.load(lol+r"\sounds\menu.mp3")
pygame.mixer.music.set_volume(0.15)
pygame.mixer.music.play(-1, 1)
clickSound = pygame.mixer.Sound(lol+'\sounds\click.ogg')
clickSound.set_volume(1)
scrollSound = pygame.mixer.Sound(lol+'\sounds\scroll.ogg')
scrollSound.set_volume(3)
runSound = pygame.mixer.Sound(lol+'\sounds\Run.ogg')
runSound.set_volume(0.2)
runSo = -1
playSoundRun = 1
playSoundSlide = 1
jumpSound = pygame.mixer.Sound(lol+'\sounds\jump.ogg')
jumpSound.set_volume(1)
dropSound = pygame.mixer.Sound(lol+'\sounds\drop.ogg')
dropSound.set_volume(0.8)
dashSound = pygame.mixer.Sound(lol+'\sounds\dash.ogg')
dashSound.set_volume(0.5)
saveSound = pygame.mixer.Sound(lol+'\sounds\save.ogg')
saveSound.set_volume(0.2)
rollbackSound = pygame.mixer.Sound(lol+'\sounds\Rollback.ogg')
rollbackSound.set_volume(3)
dieSound = pygame.mixer.Sound(lol+'\sounds\die.ogg')
dieSound.set_volume(1)
shootSound = pygame.mixer.Sound(lol+'\sounds\Shoot.ogg')
shootSound.set_volume(0.3)
misfireSound = pygame.mixer.Sound(lol+'\sounds\misfire.ogg')
misfireSound.set_volume(0.7)
chargerSound = pygame.mixer.Sound(lol+'\sounds\charger.ogg')
chargerSound.set_volume(2)
stopEnemyFlySound = pygame.mixer.Sound(lol+'\sounds\StartEnemy.ogg')
stopEnemyFlySound.set_volume(0.5)
startEnemyFlySound = pygame.mixer.Sound(lol+'\sounds\StoptEnemy.ogg')
startEnemyFlySound.set_volume(4)
hitWallSound = pygame.mixer.Sound(lol+'\sounds\hitWall.ogg')
hitWallSound.set_volume(0.6)
hitEnemSound = pygame.mixer.Sound(lol+'\sounds\hitEnem.ogg')
hitEnemSound.set_volume(0.4)
dieEnemySound = pygame.mixer.Sound(lol+'\sounds\dieEnemy.ogg')
dieEnemySound.set_volume(0.7)
finishSound = pygame.mixer.Sound(lol+'\sounds\Finish.ogg')
finishSound.set_volume(1)
lastMenuButton = ""
update_sound_volumes()
with open('textures/GGStop.txt', 'r') as file:
    text1 = file.readline()
    GGStop = ast.literal_eval(text1)
    text2 = file.readline()
    GGStopSec = ast.literal_eval(text2)
with open('textures/GGRun.txt', 'r') as file:
    text1 = file.readline()
    GGRun = ast.literal_eval(text1)
    text2 = file.readline()
    GGRunSec = ast.literal_eval(text2)
with open('textures/GGJump.txt', 'r') as file:
    text1 = file.readline()
    GGJump = ast.literal_eval(text1)
    text2 = file.readline()
    GGJumpSec = ast.literal_eval(text2)
with open('textures/GGJumpRun.txt', 'r') as file:
    text1 = file.readline()
    GGJumpRun = ast.literal_eval(text1)
    text2 = file.readline()
    GGJumpRunSec = ast.literal_eval(text2)
with open('textures/GGDash.txt', 'r') as file:
    text1 = file.readline()
    GGDash = ast.literal_eval(text1)
    text2 = file.readline()
    GGDashSec = ast.literal_eval(text2)
with open('textures/GGDashRun.txt', 'r') as file:
    text1 = file.readline()
    GGDashRun = ast.literal_eval(text1)
    text2 = file.readline()
    GGDashRunSec = ast.literal_eval(text2)
timeCadrRoll = 0
cadrRoll = 0
with open('textures/RollBack.txt', 'r') as file:
    text1 = file.readline()
    RollBackTexture = ast.literal_eval(text1)
    text2 = file.readline()
    RollBackSec = ast.literal_eval(text2)
with open('textures/RollBack2.txt', 'r') as file:
    text1 = file.readline()
    RollBackTexture2 = ast.literal_eval(text1)
    text2 = file.readline()
    RollBackSec2 = ast.literal_eval(text2)
with open('textures/Gun.txt', 'r') as file:
    text1 = file.readline()
    GUN = ast.literal_eval(text1)
    text2 = file.readline()
    GunSec = ast.literal_eval(text2)
Gun = GUN[0]
GunSurf = pygame.Surface((max(Gun[0])+2, max(Gun[1])+2), pygame.SRCALPHA)
GunSurfR = GunSurf
pivotGun = [int(-surfX + x + Size//2), int(-surfY + y + Size//2)]
offsetGun = pygame.math.Vector2(7, -3)
with open('textures/Bullets.txt', 'r') as file:
    text1 = file.readline()
    BULLETS = ast.literal_eval(text1)
with open('textures/BulletsMAX.txt', 'r') as file:
    text1 = file.readline()
    BULLETSMAX = ast.literal_eval(text1)
with open('textures/BulletTexture.txt', 'r') as file:
    text1 = file.readline()
    BulletTexture = ast.literal_eval(text1)
with open('textures/enemyFlyStan.txt', 'r') as file:
    text1 = file.readline()
    ENEMYSTAN1 = ast.literal_eval(text1)
with open('textures/dieEnemyFly.txt', 'r') as file:
    text1 = file.readline()
    ENEMYDIE1 = ast.literal_eval(text1)
with open('textures/enemyFly.txt', 'r') as file:
    text1 = file.readline()
    ENEMY1 = ast.literal_eval(text1)
    text2 = file.readline()
    enemyFlySec = ast.literal_eval(text2)
enemyFly = ENEMY1[0]
lengthSmell = HEIGHT//2 + 50
lengthFallSmell = WIDTH//2 + 50
speedEnemy = 3.5
hpEnemyFly = 100
timerStan = 3 * FPS
helpEnemy = 0
damage = 15
with open('textures/Finish.txt', 'r') as file:
    text1 = file.readline()
    FINISH = ast.literal_eval(text1)
    text2 = file.readline()
    finishSec = ast.literal_eval(text2)
finishTex = FINISH[0]
finishTimeCadr = 0
RollTex = RollBackTexture[cadrRoll]
RollTex2 = RollBackTexture2[cadrRoll]
def rotate1(surface, angle, pivot, offset):
    rotated_image = pygame.transform.rotozoom(surface, -angle, 1)  
    rotated_offset = offset.rotate(angle)  
    rect = rotated_image.get_rect(center=pivot+rotated_offset)
    return rotated_image, rect  
timeCadrSpawn = 0
timeCadrSpawn2 = 0
cadrSpawn = 0
cadrSpawn2 = 0
with open('textures/SpawnAnime.txt', 'r') as file:
    text1 = file.readline()
    SpawnTexture = ast.literal_eval(text1)
    text2 = file.readline()
    SpawnSec = ast.literal_eval(text2)
with open('textures/SpawnAnime2.txt', 'r') as file:
    text1 = file.readline()
    SpawnTexture2 = ast.literal_eval(text1)
    text2 = file.readline()
    SpawnSec2 = ast.literal_eval(text2)
SpawnTex = SpawnTexture[cadrSpawn]
SpawnTex2 = SpawnTexture2[cadrSpawn]
timeCadrSpikes = 0
cadrSpikes = 0
with open('textures/Spikes.txt', 'r') as file:
    text1 = file.readline()
    SpikesTexture = ast.literal_eval(text1)
    text2 = file.readline()
    SpikesSec = ast.literal_eval(text2)
SpikesTex = RollBackTexture[cadrRoll]
timeCadr = 0
cadr = 0
GG = GGStop[cadr]
GGRIGHT = True
DROP = False
drawX = 0
drawY = 0
anime = 0
rotate = "none"
FlagWall = False
SpringAllY = 0
timeCadrMenu = 0
cadrMenu = 0
GGMenu = GGStop[cadr]
def list_deepcopy(l):
    return [
        elem if not isinstance(elem, list) else list_deepcopy(elem)
        for elem in l
    ]
def napravl(NDash, x, y, speedG, speed):
    if NDash == "right":
        x += speedDash
        speed = maxSpeed
    elif NDash == "left":
        x -= speedDash
        speed = maxSpeed
    elif NDash == "up":
        y -= speedDash
    elif NDash == "down":
        y += speedDash
        speedG = maxSpeedG
    elif NDash == "upright":
        x += speedDash * 0.7
        y -= speedDash * 0.7
        speed = maxSpeed
    elif NDash == "upleft":
        x -= speedDash * 0.7
        y -= speedDash * 0.7
        speed = maxSpeed
    elif NDash == "downright":
        y += speedDash * 0.7
        x += speedDash * 0.7
        speedG = maxSpeedG * 0.7
        speed = maxSpeed
    elif NDash == "downleft":
        y += speedDash * 0.7
        x -= speedDash * 0.7
        speedG = maxSpeedG * 0.7
        speed = maxSpeed
    return x, y, speedG, speed
scroll = 0
victoryTime = 2 * FPS
win = False
clock = pygame.time.Clock()
while True:
    if menu == "menu":
        if buttonMenu[0] == "Играть" and letMap != "none":
            buttonMenu = ["Играть", "Карты", "Редактировать", "Создать", "Настройки", "Выйти"]
        draw_parallax_background(screen, 0, 0)
        timeCadrMenu += 1
        if timeCadrMenu >= FPS * GGStopSec // len(GGStop):
            if cadrMenu + 1 < len(GGStop):
                cadrMenu += 1
            else:
                cadrMenu = 0
            timeCadrMenu = 0
        if cadrMenu + 1 >= len(GGStop):
            cadrMenu = 0
        GGMenu = GGStop[cadrMenu]
        for j in range(len(GGMenu[0])):
            drawX = WIDTH // 2 - Size * 10 // 2 + GGMenu[0][j] * 10
            drawY = HEIGHT // 2 - Size * 10 // 2 + GGMenu[1][j] * 10
            lol = GGMenu[2][j]
            if GGMenu[2][j] == (0, 190, 0):
                lol = (50, 120, 80)
            elif GGMenu[2][j] == (0, 95, 0):
                lol = (10, 45, 20)
            pygame.draw.rect(screen, lol, (drawX, drawY, 30, 30))
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if i.type == pygame.KEYDOWN:
                if i.key == pygame.K_ESCAPE:
                    if buttonMenu[0] == "Продолжить":
                        menu = "game"
                        pygame.mixer.music.set_volume(0.06)
                        clickSound.play()
                    else:
                        pygame.quit()
                        sys.exit()
                if i.key == pygame.K_F11:
                    set_display_mode(not fullScreen)
            if i.type == pygame.MOUSEMOTION:
                mouseX = i.pos[0] * k_posX
                mouseY = i.pos[1] * k_posY
            if i.type == pygame.MOUSEBUTTONUP:
                if i.button == 1:
                    for j in range(len(buttonMenu)):
                        text = menuFont.render(buttonMenu[j], 1, WHITE)
                        if i.pos[0] * k_posX > WIDTH//2-text.get_width()//2 \
                                and i.pos[0] * k_posX < WIDTH//2-text.get_width()//2+text.get_width() \
                                and i.pos[1] * k_posY > HEIGHT//2-50+j*(text.get_height()+5)+5 \
                                and i.pos[1] * k_posY < HEIGHT // 2 - 50 + j * (text.get_height() + 5) + text.get_height()-5:
                            clickSound.play()
                            if buttonMenu[j] == "Играть":
                                menu = "game"
                                canCreate = False
                                gameMode = "surv"
                                victoryTime = 2 * FPS
                                pygame.mixer.music.set_volume(0.06)
                                start_level_timer(letMap.split(".")[0])
                                break
                            elif buttonMenu[j] == "Продолжить":
                                menu = "game"
                                pygame.mixer.music.set_volume(0.06)
                                pause_off()
                                break
                            elif buttonMenu[j] == "Карты" or buttonMenu[j] == "Список карт":
                                menu = "maps"
                                lol = os.path.dirname(os.path.abspath(__file__))
                                directory = lol+"/maps"
                                files = os.listdir(directory)
                                print(files)
                                break
                            elif buttonMenu[j] == "Сохранить":
                                if "enemyFly" in map:
                                    for ret in range(len(map["enemyFly"][0])):
                                        map["enemyFly"][-1][ret] = 0
                                        map["enemyFly"][4][ret] = 0
                                        map["enemyFly"][5][ret] = 0
                                        map["enemyFly"][6][ret] = False
                                        map["enemyFly"][0][ret] = map["enemyFly"][7][0][ret]
                                        map["enemyFly"][1][ret] = map["enemyFly"][7][1][ret]
                                        map["enemyFly"][7][2][ret] = 0
                                        map["enemyFly"][7][3][ret] = 0
                                        map["enemyFly"][8][ret] = 0
                                        map["enemyFly"][9][ret] = hpEnemyFly
                                if "bullets" in map:
                                    for ret in range(len(map["bullets"][0])):
                                        map["bullets"][0][ret] = map["bullets"][4][ret]
                                        map["bullets"][1][ret] = map["bullets"][5][ret]
                                lol = os.path.dirname(os.path.abspath(__file__))
                                directory = lol + "/maps"
                                files = os.listdir(directory)
                                my_file = open(directory+"/map"+str(len(files)+1)+".txt", "w+")
                                my_file.write(str(map)+"\n"+str(spawnX)+"\n"+str(spawnY)+"\n"+str(spawnSX)+"\n"+str(spawnSY))
                                break
                            elif buttonMenu[j] == "Настройки":
                                menu = "settings"
                                buttonMenu = ["Управление", "Звук", "Сбросить настройки", "Назад"]
                                break
                            elif buttonMenu[j] == "Редактировать":
                                victoryTime = 2 * FPS
                                pygame.mixer.music.set_volume(0.06)
                                menu = "game"
                                canCreate = True
                                gameMode = "surv"
                                createType = "block"
                                correctObject = {"block": [], "spikes": [], "spring": [], "rollback": [],
                                                 "background": [], "spawnpoint": [], "bullets": [], "enemyFly": [], "finish": []}
                                break
                            elif buttonMenu[j] == "Создать":
                                victoryTime = 2 * FPS
                                pygame.mixer.music.set_volume(0.06)
                                menu = "game"
                                gameMode = "surv"
                                canCreate = True
                                x = spawnX
                                y = spawnY
                                xO = x
                                yO = y
                                surfX = spawnSX
                                surfY = spawnSY
                                motionL = 'stop'
                                motionR = 'stop'
                                motionU = 'stop'
                                motionD = 'stop'
                                dash = 'stop'
                                jump = 'stop'
                                jumpWallL = "stop"
                                jumpWallR = "stop"
                                speed = 0
                                speedG = 0
                                timeDash = 0
                                canJump = False
                                canJumpWallR = False
                                canJumpWallL = False
                                canDash = False
                                map = {"block": [[], [], [], []], "spikes": [[], [], [], []], "spring": [[], [], [], []],
                                      "rollback": [[], [], 8, 8, []], "background": [[], [], [], [], []],
                                      "spawnpoint": [[], [], 21, 21, -1], "bullets": [[], [], 15, 15, [], []],
                                       "enemyFly": [[], [], 21, 21, [], [], [], [[], [], [], []], [], [], []], "finish": [[], [], 24, 24]}
                                correctObject = {"block": [], "spikes": [], "spring": [], "rollback": [],
                                                 "background": [], "spawnpoint": [], "bullets": [], "enemyFly": [], "finish": []}
                                letMap = "none"
                                createType = "block"
                                break
                            elif buttonMenu[j] == "Покинуть уровень" or  buttonMenu[j] == "Поплакать" or buttonMenu[j] == "Выход в главное меню":
                                victoryTime = 2 * FPS
                                menu = "menu"
                                buttonMenu = ["Играть", "Карты", "Создать", "Настройки", "Выйти"]
                                canCreate = True
                                spawnX = TrueX
                                spawnY = TrueY
                                x = spawnX
                                y = spawnY
                                xO = x
                                yO = y
                                surfX = 0
                                surfY = 0
                                spawnSX = surfX
                                spawnSY = surfY
                                motionL = 'stop'
                                motionR = 'stop'
                                motionU = 'stop'
                                motionD = 'stop'
                                dash = 'stop'
                                jump = 'stop'
                                jumpWallL = "stop"
                                jumpWallR = "stop"
                                speed = 0
                                maxSpeed = 4
                                speedG = 0
                                timeDash = 0
                                canJump = False
                                canJumpWallR = False
                                canJumpWallL = False
                                canDash = False
                                canShoot = True
                                timeShoot = 0
                                bullets = 0
                                bulletsCadr = bullets * 2
                                bulletTime = 0
                                colorBullets = colorBullets2
                                map = {"block": [[], [], [], []], "spikes": [[], [], [], []], "spring": [[], [], [], []],
                                      "rollback": [[], [], 8, 8, []], "background": [[], [], [], [], []],
                                      "spawnpoint": [[], [], 21, 21, -1], "bullets": [[], [], 15, 15, [], []],
                                       "enemyFly": [[], [], 21, 21, [], [], [], [[], [], [], []], [], [], []], "finish": [[], [], 24, 24]}
                                correctObject = {"block": [], "spikes": [], "spring": [], "rollback": [],
                                                 "background": [], "spawnpoint": [], "bullets": [], "enemyFly": [], "finish": []}
                                letMap = "none"
                                createType = "block"
                                letMap = "none"
                                break
                            elif buttonMenu[j] == "Выйти":
                                pygame.quit()
                                sys.exit()
        textMENU = fontMENU.render('МЕНЮ', 1, GREEN_d)
        screen.blit(textMENU, (WIDTH//2-textMENU.get_width()//2, HEIGHT//4))
        if buttonMenu[0] == "Поплакать" or buttonMenu[0] == "Покинуть уровень" or buttonMenu[0] == "Выход в главное меню":
            if win[0]:
                colorWin = (0, 255, 0)
                textWinGame = "НОВЫЙ РЕКОРД:"
                best_time = settings["statistics"]["level_times"][letMap.split(".")[0]]
                textWinGame += f" | Время: {format_time(best_time)}"
            else:
                colorWin = (255, 0, 0)
                textWinGame = ""
                textWinGame += f"Время: {format_time(win[1])}"
            textWin = menuFont.render(textWinGame, 1, colorWin)
            screen.blit(textWin, (WIDTH // 2 - textWin.get_width() // 2, HEIGHT // 4 - 50))
        for i in range(len(buttonMenu)):
            colorButton = WHITE
            text = menuFont.render(buttonMenu[i], 1, colorButton)
            if mouseX > WIDTH // 2 - text.get_width() // 2 \
                    and mouseX < WIDTH // 2 - text.get_width() // 2 + text.get_width() \
                    and mouseY > HEIGHT // 2 - 50 + i * (text.get_height() + 5) +5 \
                    and mouseY < HEIGHT // 2 - 50 + i * (text.get_height() + 5) + text.get_height() -5:
                if lastMenuButton != buttonMenu[i]:
                    scrollSound.play()
                    lastMenuButton = buttonMenu[i]
                colorButton = (255, 0, 0)
            text = menuFont.render(buttonMenu[i], 1, colorButton)
            screen.blit(text, (WIDTH//2-text.get_width()//2, HEIGHT//2-50+i*(text.get_height()+5)))
            if buttonMenu[i] == "Играть" and colorButton == (255, 0, 0):
                textMap = menuFont.render(">"+letMap.split(".")[0], 1, (200, 200, 10))
                screen.blit(textMap, (WIDTH // 2 + text.get_width() // 2+5, HEIGHT // 2 - 50 + i * (text.get_height() + 5)))
            if buttonMenu[i] == "Редактировать" and colorButton == (255, 0, 0):
                textMap = menuFont.render(">" + letMap.split(".")[0], 1, (200, 200, 10))
                screen.blit(textMap,
                            (WIDTH // 2 + text.get_width() // 2 + 5, HEIGHT // 2 - 50 + i * (text.get_height() + 5)))
            if buttonMenu[i] == "Сохранить" and colorButton == (255, 0, 0):
                lol = os.path.dirname(os.path.abspath(__file__))
                directory = lol + "/maps"
                files = os.listdir(directory)
                textMap = menuFont.render(">map" + str(len(files)+1), 1, (200, 200, 10))
                screen.blit(textMap,
                            (WIDTH // 2 + text.get_width() // 2 + 5, HEIGHT // 2 - 50 + i * (text.get_height() + 5)))
    elif menu == "settings":
        draw_parallax_background(screen, 0, 0)
        timeCadrMenu += 1
        if timeCadrMenu >= FPS * SpawnSec2 // len(SpawnTexture2):
            if cadrMenu + 1 < len(SpawnTexture2):
                cadrMenu += 1
            else:
                cadrMenu = 0
            timeCadrMenu = 0
        if cadrMenu + 1 >= len(SpawnTexture2):
            cadrMenu = 0
        GGMenu = SpawnTexture2[cadrMenu]
        for j in range(len(GGMenu[0])):
            drawX = WIDTH // 2 - Size * 10 // 2 + GGMenu[0][j] * 10
            drawY = HEIGHT // 2 - Size * 10 // 2 + GGMenu[1][j] * 10
            lol = GGMenu[2][j]
            if GGMenu[2][j] == (0, 190, 0):
                lol = (50, 120, 80)
            elif GGMenu[2][j] == (0, 95, 0):
                lol = (10, 45, 20)
            elif GGMenu[2][j] == (125, 250, 135):
                lol = (50, 120, 80)
            elif GGMenu[2][j] == (220, 215, 0):
                lol = (201, 168, 58)
            pygame.draw.rect(screen, lol, (drawX, drawY, 30, 30))
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if i.type == pygame.KEYDOWN:
                if i.key == pygame.K_ESCAPE:
                    waitingForKey = False
                    selectedKeyAction = ""
                    if buttonMenu[0] == "Управление":
                        menu = "menu"
                        buttonMenu = ["Играть", "Карты", "Создать", "Настройки", "Выйти"]
                    else:
                        buttonMenu = ["Управление", "Звук", "Сбросить настройки", "Назад"]
                    clickSound.play()
                if i.key == pygame.K_F11:
                    set_display_mode(not fullScreen)
                if waitingForKey and i.key != pygame.K_ESCAPE:
                    new_key = i.key
                    conflict = False
                    for action, key in settings["keys"].items():
                        if key == new_key and action != selectedKeyAction:
                            conflict = True
                            break
                    if not conflict:
                        settings["keys"][selectedKeyAction] = new_key
                        globals()[selectedKeyAction] = new_key
                        save_settings(settings)
                        if buttonMenu and (buttonMenu[0].startswith("UP:") or buttonMenu[0].startswith("Вверх:")):
                            buttonMenu = [
                                f"UP: {get_key_name(settings['keys']['UP'])}",
                                f"DOWN: {get_key_name(settings['keys']['DOWN'])}",
                                f"LEFT: {get_key_name(settings['keys']['LEFT'])}",
                                f"RIGHT: {get_key_name(settings['keys']['RIGHT'])}",
                                f"JUMP: {get_key_name(settings['keys']['JUMP'])}",
                                f"DASH: {get_key_name(settings['keys']['DASH'])}",
                                f"SHOOT: {get_key_name(settings['keys']['SHOOT'])}",
                                "Назад"
                            ]
                    waitingForKey = False
                    selectedKeyAction = ""
            if i.type == pygame.MOUSEMOTION:
                mouseX = i.pos[0] * k_posX
                mouseY = i.pos[1] * k_posY
                if dragging_slider:
                    slider_x = WIDTH // 2 - 100
                    slider_width = 200
                    if mouseX >= slider_x and mouseX <= slider_x + slider_width:
                        click_pos = mouseX - slider_x
                        new_volume = int((click_pos / slider_width) * 100)
                        new_volume = max(0, min(100, new_volume))
                        if dragging_type == "music":
                            settings["sound"]["music_volume"] = new_volume
                        elif dragging_type == "sfx":
                            settings["sound"]["sfx_volume"] = new_volume
                        update_sound_volumes()
                        save_settings(settings)
                        buttonMenu = [
                            f"Музыка: {settings['sound']['music_volume']}%",
                            f"Звуки: {settings['sound']['sfx_volume']}%",
                            "Назад"
                        ]
            if i.type == pygame.MOUSEBUTTONUP:
                if i.button == 1:
                    dragging_slider = False
                    dragging_type = ""
                    extra_spacing = 25 if "Музыка:" in str(buttonMenu) or "Звуки:" in str(buttonMenu) else 0
                    for j in range(len(buttonMenu)):
                        text = menuFont.render(buttonMenu[j], 1, WHITE)
                        item_height = text.get_height() + 5 + extra_spacing
                        if i.pos[0] * k_posX > WIDTH//2-text.get_width()//2 \
                                and i.pos[0] * k_posX < WIDTH//2-text.get_width()//2+text.get_width() \
                                and i.pos[1] * k_posY > HEIGHT//2-50+j*item_height+5 \
                                and i.pos[1] * k_posY < HEIGHT // 2 - 50 + j * item_height + text.get_height()-5:
                            if not((buttonMenu[j].split(":")[0] == "Музыка") or (buttonMenu[j].split(":")[0] == "Звуки")):
                                clickSound.play()
                            if buttonMenu[j] == "Назад":
                                if buttonMenu[0] == "Управление":
                                    menu = "menu"
                                    buttonMenu = ["Играть", "Карты", "Создать", "Настройки", "Выйти"]
                                else:
                                    buttonMenu = ["Управление", "Звук", "Сбросить настройки", "Назад"]
                                waitingForKey = False
                                selectedKeyAction = ""
                                break
                            elif buttonMenu[j] == "Управление":
                                buttonMenu = [
                                    f"UP: {get_key_name(settings['keys']['UP'])}",
                                    f"DOWN: {get_key_name(settings['keys']['DOWN'])}",
                                    f"LEFT: {get_key_name(settings['keys']['LEFT'])}",
                                    f"RIGHT: {get_key_name(settings['keys']['RIGHT'])}",
                                    f"JUMP: {get_key_name(settings['keys']['JUMP'])}",
                                    f"DASH: {get_key_name(settings['keys']['DASH'])}",
                                    f"SHOOT: {get_key_name(settings['keys']['SHOOT'])}",
                                    "Назад"
                                ]
                                break
                            elif buttonMenu[j] == "Звук":
                                buttonMenu = [
                                    f"Музыка: {settings['sound']['music_volume']}%",
                                    f"Звуки: {settings['sound']['sfx_volume']}%",
                                    "Назад"
                                ]
                                break
                            elif buttonMenu[j] == "Сбросить настройки":
                                settings["fullscreen"] = True
                                settings["keys"] = {
                                    "UP": pygame.K_w,
                                    "DOWN": pygame.K_s,
                                    "LEFT": pygame.K_a,
                                    "RIGHT": pygame.K_d,
                                    "JUMP": pygame.K_SPACE,
                                    "DASH": pygame.K_RSHIFT,
                                    "SHOOT": "MOUSE_1"
                                }
                                settings["sound"] = {
                                    "music_volume": 15,
                                    "sfx_volume": 100
                                }
                                init_keys()
                                update_sound_volumes()
                                save_settings(settings)
                                buttonMenu = ["Управление", "Звук", "Сбросить настройки", "Назад"]
                                break
                            elif buttonMenu[j].startswith("UP:"):
                                waitingForKey = True
                                selectedKeyAction = "UP"
                                break
                            elif buttonMenu[j].startswith("DOWN:"):
                                waitingForKey = True
                                selectedKeyAction = "DOWN"
                                break
                            elif buttonMenu[j].startswith("LEFT:"):
                                waitingForKey = True
                                selectedKeyAction = "LEFT"
                                break
                            elif buttonMenu[j].startswith("RIGHT:"):
                                waitingForKey = True
                                selectedKeyAction = "RIGHT"
                                break
                            elif buttonMenu[j].startswith("JUMP:"):
                                waitingForKey = True
                                selectedKeyAction = "JUMP"
                                break
                            elif buttonMenu[j].startswith("DASH:"):
                                waitingForKey = True
                                selectedKeyAction = "DASH"
                                break
                            elif buttonMenu[j].startswith("SHOOT:"):
                                waitingForKey = True
                                selectedKeyAction = "SHOOT"
                                break
            if i.type == pygame.MOUSEBUTTONDOWN:
                if i.button == 1:
                    for j in range(len(buttonMenu)):
                        if buttonMenu[j].startswith("Музыка:") or buttonMenu[j].startswith("Звуки:"):
                            extra_spacing = 25 if "Музыка:" in str(buttonMenu) or "Звуки:" in str(buttonMenu) else 0
                            item_height = menuFont.get_height() + 5 + extra_spacing
                            slider_x = WIDTH // 2 - 100
                            slider_y = HEIGHT // 2 - 50 + j * item_height + menuFont.get_height() + 8
                            slider_width = 200
                            slider_height = 20
                            if (i.pos[0] * k_posX >= slider_x and i.pos[0] * k_posX <= slider_x + slider_width and
                                i.pos[1] * k_posY >= slider_y and i.pos[1] * k_posY <= slider_y + slider_height):
                                dragging_slider = True
                                if buttonMenu[j].startswith("Музыка:"):
                                    dragging_type = "music"
                                else:
                                    dragging_type = "sfx"
                                click_pos = i.pos[0] * k_posX - slider_x
                                new_volume = int((click_pos / slider_width) * 100)
                                new_volume = max(0, min(100, new_volume))
                                if dragging_type == "music":
                                    settings["sound"]["music_volume"] = new_volume
                                elif dragging_type == "sfx":
                                    settings["sound"]["sfx_volume"] = new_volume
                                update_sound_volumes()
                                save_settings(settings)
                                buttonMenu = [
                                    f"Музыка: {settings['sound']['music_volume']}%",
                                    f"Звуки: {settings['sound']['sfx_volume']}%",
                                    "Назад"
                                ]
                                break
                if waitingForKey:
                    mouse_key = f"MOUSE_{i.button}"
                    conflict = False
                    for action, key in settings["keys"].items():
                        if key == mouse_key and action != selectedKeyAction:
                            conflict = True
                            break
                    if not conflict:
                        settings["keys"][selectedKeyAction] = mouse_key
                        globals()[selectedKeyAction] = mouse_key
                        save_settings(settings)
                        if buttonMenu and buttonMenu[0].startswith("UP:"):
                            buttonMenu = [
                                f"UP: {get_key_name(settings['keys']['UP'])}",
                                f"DOWN: {get_key_name(settings['keys']['DOWN'])}",
                                f"LEFT: {get_key_name(settings['keys']['LEFT'])}",
                                f"RIGHT: {get_key_name(settings['keys']['RIGHT'])}",
                                f"JUMP: {get_key_name(settings['keys']['JUMP'])}",
                                f"DASH: {get_key_name(settings['keys']['DASH'])}",
                                f"SHOOT: {get_key_name(settings['keys']['SHOOT'])}",
                                "Назад"
                            ]
                    waitingForKey = False
                    selectedKeyAction = ""
        textMENU = fontMENU.render('НАСТРОЙКИ', 1, GREEN_d)
        screen.blit(textMENU, (WIDTH//2-textMENU.get_width()//2, HEIGHT//4))
        if waitingForKey:
            textWait = menuFont.render(f"Нажмите клавишу для {selectedKeyAction}...", 1, (0, 255, 0))
            screen.blit(textWait, (WIDTH//2-textWait.get_width()//2, HEIGHT//4 - 50))
        for i in range(len(buttonMenu)):
            colorButton = WHITE
            text = menuFont.render(buttonMenu[i], 1, colorButton)
            extra_spacing = 0
            if "Музыка:" in str(buttonMenu) or "Звуки:" in str(buttonMenu):
                extra_spacing = 25
            item_height = text.get_height() + 5 + extra_spacing
            if mouseX > WIDTH // 2 - text.get_width() // 2 \
                    and mouseX < WIDTH // 2 - text.get_width() // 2 + text.get_width() \
                    and mouseY > HEIGHT // 2 - 50 + i * item_height +5 \
                    and mouseY < HEIGHT // 2 - 50 + i * item_height + text.get_height() -5:
                if lastMenuButton != buttonMenu[i]:
                    if not ((buttonMenu[i].split(":")[0] == "Музыка") or (buttonMenu[i].split(":")[0] == "Звуки")):
                        scrollSound.play()
                        lastMenuButton = buttonMenu[i]
                if not((buttonMenu[i].split(":")[0] == "Музыка") or (buttonMenu[i].split(":")[0] == "Звуки")):
                    colorButton = (255, 0, 0)
            if waitingForKey and selectedKeyAction == buttonMenu[i].split(":")[0]:
                colorButton = (0, 255, 0)
            text = menuFont.render(buttonMenu[i], 1, colorButton)
            screen.blit(text, (WIDTH//2-text.get_width()//2, HEIGHT//2-50+i*item_height))
            if buttonMenu[i].startswith("Музыка:") or buttonMenu[i].startswith("Звуки:"):
                slider_x = WIDTH // 2 - 100
                slider_y = HEIGHT // 2 - 50 + i * item_height + text.get_height() + 8
                slider_width = 200
                slider_height = 10
                if buttonMenu[i].startswith("Музыка:"):
                    current_value = settings["sound"]["music_volume"]
                else:
                    current_value = settings["sound"]["sfx_volume"]
                pygame.draw.rect(screen, (100, 100, 100), (slider_x, slider_y, slider_width, slider_height))
                filled_width = int((current_value / 100) * slider_width)
                pygame.draw.rect(screen, (0, 150, 255), (slider_x, slider_y, filled_width, slider_height))
                handle_x = slider_x + filled_width - 5
                handle_y = slider_y - 5
                pygame.draw.rect(screen, WHITE, (handle_x, handle_y, 10, slider_height + 10))
            if buttonMenu[i] == "Играть" and colorButton == (255, 0, 0):
                textMap = menuFont.render(">"+letMap, 1, (200, 200, 10))
                screen.blit(textMap, (WIDTH // 2 + text.get_width() // 2+5, HEIGHT // 2 - 50 + i * (text.get_height() + 5)))
    elif menu == "maps":
        draw_parallax_background(screen, 0, 0)
        timeCadrMenu += 1
        if timeCadrMenu >= FPS * GGRunSec // len(GGRun):
            if cadrMenu + 1 < len(GGRun):
                cadrMenu += 1
            else:
                cadrMenu = 0
            timeCadrMenu = 0
        if cadrMenu + 1 >= len(GGRun):
            cadrMenu = 0
        GGMenu = GGRun[cadrMenu]
        for j in range(len(GGMenu[0])):
            drawX = WIDTH // 2 - Size * 10 // 2 + GGMenu[0][j] * 10
            drawY = HEIGHT // 2 - Size * 10 // 2 + GGMenu[1][j] * 10
            lol = GGMenu[2][j]
            if GGMenu[2][j] == (0, 190, 0):
                lol = (50, 120, 80)
            elif GGMenu[2][j] == (0, 95, 0):
                lol = (10, 45, 20)
            pygame.draw.rect(screen, lol, (drawX, drawY, 30, 30))
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if i.type == pygame.KEYDOWN:
                if i.key == pygame.K_ESCAPE:
                    menu = "menu"
                    scroll = 0
                    clickSound.play()
                if i.key == pygame.K_F11:
                    set_display_mode(not fullScreen)
            if i.type == pygame.MOUSEMOTION:
                mouseX = i.pos[0] * k_posX
                mouseY = i.pos[1] * k_posY
            if i.type == pygame.MOUSEBUTTONUP:
                if i.button == 1:
                    for j in range(len(files[scroll:])):
                        text = menuFont.render(files[j+scroll].split(".")[0], 1, WHITE)
                        if i.pos[0] * k_posX > WIDTH // 2 - text.get_width() // 2 \
                                and i.pos[0] * k_posX < WIDTH // 2 - text.get_width() // 2 + text.get_width() \
                                and i.pos[1] * k_posY > HEIGHT // 2 - 50 + j * (text.get_height() + 5) + 5 \
                                and i.pos[1] * k_posY < HEIGHT // 2 - 50 + j * (text.get_height() + 5) + text.get_height() - 5:
                            clickSound.play()
                            with open('maps/'+files[j+scroll], 'r') as file:
                                text1 = file.readline()
                                map = ast.literal_eval(text1)
                                text2 = file.readline()
                                x = ast.literal_eval(text2)
                                text3 = file.readline()
                                y = ast.literal_eval(text3)
                                text4 = file.readline()
                                surfX = ast.literal_eval(text4)
                                text5 = file.readline()
                                surfY = ast.literal_eval(text5)
                            spawnX = x
                            spawnY = y
                            spawnSX = surfX
                            spawnSY = surfY
                            letMap = files[j+scroll]
                            menu = "menu"
                            scroll = 0
            if i.type == pygame.MOUSEBUTTONDOWN:
                if i.button == 4:
                    if scroll > 0:
                        scrollSound.play()
                        scroll -= 1
                if i.button == 5:
                    if scroll < len(files) - 7:
                        scrollSound.play()
                        scroll += 1
        fps = int(clock.get_fps())
        textEsc = font.render('Esc', 1, WHITE)
        screen.blit(textEsc, (WIDTH-textEsc.get_width()-10, +10))
        textMENU = fontMENU.render('КАРТЫ', 1, GREEN_d)
        screen.blit(textMENU, (WIDTH // 2 - textMENU.get_width() // 2, HEIGHT // 4))
        for i in range(len(files[scroll:])):
            colorButton = WHITE
            if mouseX > WIDTH // 2 - text.get_width() // 2 \
                    and mouseX < WIDTH // 2 - text.get_width() // 2 + text.get_width() \
                    and mouseY > HEIGHT // 2 - 50 + i * (text.get_height() + 5) + 5 \
                    and mouseY < HEIGHT // 2 - 50 + i * (text.get_height() + 5) + text.get_height() - 5:
                if lastMenuButton != files[i+scroll]:
                    scrollSound.play()
                    lastMenuButton = files[i+scroll]
                colorButton = (255, 0, 0)
            text = menuFont.render(files[i+scroll].split(".")[0], 1, colorButton)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50 + i * (text.get_height() + 5)))
            level_name = files[i+scroll].split(".")[0]
            stats_text = ""
            if level_name in settings["statistics"]["level_times"]:
                best_time = settings["statistics"]["level_times"][level_name]
                stats_text += f" Время: {format_time(best_time)}"
            if level_name in settings["statistics"]["level_deaths"]:
                deaths = settings["statistics"]["level_deaths"][level_name]
                stats_text += f" | Смерти: {deaths}"
            stats_color = (200, 200, 10) if colorButton == (255, 0, 0) else (150, 150, 150)
            stats_render = font.render(stats_text, 1, stats_color)
            screen.blit(stats_render,
                        (WIDTH // 2 + text.get_width() // 2 + 10, HEIGHT // 2 - 50 + i * (text.get_height() + 5) + 5))
    elif menu == "game":
        '''if gameMode == "surv":
            pygame.mouse.set_visible(False)
        else:
            pygame.mouse.set_visible(True)'''
        draw_parallax_background(screen, surfX, surfY)
        grav = 1
        stopRun = 0
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if i.type == pygame.KEYDOWN:
                if i.key == pygame.K_ESCAPE and victoryTime == 2 * FPS:
                    pygame.mixer.music.unpause()
                    pygame.mixer.music.set_volume(0.15)
                    if canCreate == False:
                        pause_on()
                        buttonMenu = ["Продолжить", "Покинуть уровень"]
                    else:
                        buttonMenu = ["Продолжить", "Сохранить", "Покинуть уровень"]
                    menu = "menu"
                if i.key == pygame.K_F11:
                    set_display_mode(not fullScreen)
                if i.key == UP:
                    motionU = "motion"
                    motionD = "stop"
                if i.key == DOWN:
                    motionD = "motion"
                    motionU = "stop"
                if i.key == LEFT:
                    motionL = "motion"
                    motionR = "stop"
                    lastButton = "left"
                if i.key == RIGHT:
                    motionR = "motion"
                    motionL = "stop"
                    lastButton = "right"
                if i.key == JUMP:
                    if canJump:
                        jump = "motion"
                        canJump = False
                        speedG = 0
                        jumpSound.play()
                    if canJumpWallL:
                        jumpWallL = "motion"
                        jump = "stop"
                        canJumpWallL = False
                        speedG = 0
                        spring = 0
                        jumpSound.play()
                    elif canJumpWallR:
                        jumpWallR = "motion"
                        jump = "stop"
                        canJumpWallR = False
                        speedG = 0
                        spring = 0
                        jumpSound.play()
                if i.key == DASH:
                    if canDash:
                        dash = "motion"
                        jump = "stop"
                        jumpWallL = "stop"
                        jumpWallR = "stop"
                        speedJ = J
                        canDash = False
                        speedG = 0
                        grav = 0
                        dashSound.play()
                        if motionU == "motion" and motionR == "motion":
                            NDash = "upright"
                        elif motionU == "motion" and motionL == "motion":
                            NDash = "upleft"
                        elif motionD == "motion" and motionR == "motion":
                            NDash = "downright"
                        elif motionD == "motion" and motionL == "motion":
                            NDash = "downleft"
                        elif motionU == "motion":
                            NDash = "up"
                        elif motionD == "motion":
                            NDash = "down"
                        elif motionL == "motion":
                            NDash = "left"
                        elif motionR == "motion":
                            NDash = "right"
                        else:
                            NDash = lastButton
                if canCreate:
                    if i.key == pygame.K_g:
                        if gameMode == "surv":
                            gameMode = "creat"
                            if "enemyFly" in map:
                                for ret in range(len(map["enemyFly"][0])):
                                    map["enemyFly"][-1][ret] = 0
                                    map["enemyFly"][4][ret] = 0
                                    map["enemyFly"][5][ret] = 0
                                    map["enemyFly"][6][ret] = False
                                    map["enemyFly"][0][ret] = map["enemyFly"][7][0][ret]
                                    map["enemyFly"][1][ret] = map["enemyFly"][7][1][ret]
                                    map["enemyFly"][7][2][ret] = 0
                                    map["enemyFly"][7][3][ret] = 0
                                    map["enemyFly"][8][ret] = 0
                                    map["enemyFly"][9][ret] = hpEnemyFly
                            if "bullets" in map:
                                for ret in range(len(map["bullets"][0])):
                                    map["bullets"][0][ret] = map["bullets"][4][ret]
                                    map["bullets"][1][ret] = map["bullets"][5][ret]
                            pygame.mixer.music.pause()
                        else:
                            gameMode = "surv"
                            pygame.mixer.music.unpause()
                if gameMode == "creat":
                    if i.key == pygame.K_DELETE:
                        for j in range(len(map["enemyFly"]) + 3):
                            if j < 4:
                                lol = 0
                                for n in range(len(correctObject["block"])):
                                    map["block"][j].pop(correctObject["block"][n+lol])
                                    lol -= 1
                                lol = 0
                                for n in range(len(correctObject["spikes"])):
                                    map["spikes"][j].pop(correctObject["spikes"][n+lol])
                                    lol -= 1
                                lol = 0
                                for n in range(len(correctObject["spring"])):
                                    map["spring"][j].pop(correctObject["spring"][n+lol])
                                    lol -= 1
                            if j < 5:
                                lol = 0
                                for n in range(len(correctObject["background"])):
                                    map["background"][j].pop(correctObject["background"][n+lol])
                                    lol -= 1
                                try:
                                    lol = 0
                                    for n in range(len(correctObject["rollback"])):
                                        map["rollback"][j].pop(correctObject["rollback"][n+lol])
                                        lol -= 1
                                except:
                                    pass
                                try:
                                    lol = 0
                                    for n in range(len(correctObject["spawnpoint"])):
                                        map["spawnpoint"][j].pop(correctObject["spawnpoint"][n+lol])
                                        lol -= 1
                                except:
                                    pass
                                try:
                                    lol = 0
                                    for n in range(len(correctObject["finish"])):
                                        map["finish"][j].pop(correctObject["finish"][n+lol])
                                        lol -= 1
                                except:
                                    pass
                            try:
                                lol = 0
                                for n in range(len(correctObject["bullets"])):
                                    map["bullets"][j].pop(correctObject["bullets"][n+lol])
                                    lol -= 1
                            except:
                                pass
                            try:
                                lol = 0
                                for n in range(len(correctObject["enemyFly"])):
                                    if j >= 7 and j <= 10:
                                        map["enemyFly"][7][j-7].pop(correctObject["enemyFly"][n + lol])
                                    else:
                                        map["enemyFly"][j].pop(correctObject["enemyFly"][n+lol])
                                    lol -= 1
                            except:
                                pass
                        correctObject = {"block": [], "spikes": [], "spring": [], "rollback": [], "background": [],
                                         "spawnpoint": [], "bullets": [], "enemyFly": [], "finish": []}
                        print("\nmap =", map)
                    elif i.key == pygame.K_p:
                        map["spawnpoint"][4] = -1
                        spawnX = x
                        spawnY = y
                        spawnSX = surfX
                        spawnSY = surfY
                    elif i.key == pygame.K_1:
                        createType = 'block'
                    elif i.key == pygame.K_2:
                        createType = 'spikes'
                    elif i.key == pygame.K_3:
                        createType = 'spring'
                    elif i.key == pygame.K_4:
                        createType = 'rollback'
                    elif i.key == pygame.K_5:
                        createType = 'spawnpoint'
                    elif i.key == pygame.K_6:
                        createType = 'bullets'
                    elif i.key == pygame.K_7:
                        createType = 'enemyFly'
                    elif i.key == pygame.K_8:
                        createType = 'finish'
                    '''if i.key == pygame.K_0:
                        createType = 'background'
                    if i.key == pygame.K_F1:
                        createColor = backColor[5]
                    if i.key == pygame.K_F2:
                        createColor = backColor[4]
                    if i.key == pygame.K_F3:
                        createColor = backColor[3]
                    if i.key == pygame.K_F4:
                        createColor = backColor[2]
                    if i.key == pygame.K_F5:
                        createColor = backColor[1]
                    if i.key == pygame.K_F6:
                        createColor = backColor[0]'''
            if i.type == pygame.KEYUP:
                if i.key == pygame.K_w:
                    motionU = "stop"
                if i.key == pygame.K_s:
                    motionD = "stop"
                if i.key == pygame.K_a:
                    motionL = "stop"
                    speed = 0
                if i.key == pygame.K_d:
                    motionR = "stop"
                    speed = 0
                if i.key == pygame.K_SPACE:
                    if jump == "motion" or jumpWallL == "motion" or jumpWallR == "motion":
                        if spring == 0:
                            jump = "stop"
                            jumpWallL = "stop"
                            jumpWallR = "stop"
                            speedG = 0
            if i.type == pygame.MOUSEBUTTONDOWN:
                if isinstance(DASH, str) and len(DASH.split("_")) > 1:
                    if i.button == int(DASH.split("_")[1]) and gameMode == "surv":
                        if canDash:
                            dash = "motion"
                            jump = "stop"
                            jumpWallL = "stop"
                            jumpWallR = "stop"
                            speedJ = J
                            canDash = False
                            speedG = 0
                            grav = 0
                            dashSound.play()
                            if motionU == "motion" and motionR == "motion":
                                NDash = "upright"
                            elif motionU == "motion" and motionL == "motion":
                                NDash = "upleft"
                            elif motionD == "motion" and motionR == "motion":
                                NDash = "downright"
                            elif motionD == "motion" and motionL == "motion":
                                NDash = "downleft"
                            elif motionU == "motion":
                                NDash = "up"
                            elif motionD == "motion":
                                NDash = "down"
                            elif motionL == "motion":
                                NDash = "left"
                            elif motionR == "motion":
                                NDash = "right"
                            else:
                                NDash = lastButton
                if isinstance(SHOOT, str) and len(SHOOT.split("_")) > 1:
                    if i.button == int(SHOOT.split("_")[1]) and gameMode == "surv":
                        if canShoot and bullets > 0:
                            shootSound.play()
                            shoot = "motion"
                            canShoot = False
                            bullets -= 1
                            bulletTime = 20
                            timeShoot = GunSec * FPS
                            if bullets == 0:
                                colorBullets = colorBullets2
                        elif bullets <= 0 and canShoot:
                            misfireSound.play()
                if i.button == 1:
                    if gameMode == "creat":
                        if createType != "rollback" and createType != "spawnpoint" and createType != "bullets" and createType != "enemyFly" and createType != "finish":
                            map[createType][0].append(int(i.pos[0] * k_posX+surfX) - int(i.pos[0] * k_posX+surfX) % 10)
                            map[createType][1].append(int(i.pos[1] * k_posY+surfY) - int(i.pos[1] * k_posY+surfY) % 10)
                        draw = 1
                elif i.button == 3:
                    if gameMode == "creat":
                        firstMouseX = i.pos[0] * k_posX
                        firstMouseY = i.pos[1] * k_posY
                        draw = 2
            if i.type == pygame.MOUSEMOTION:
                if gameMode == "creat":
                    if createType != "rollback" and createType != "spawnpoint" and createType != "bullets" and createType != "enemyFly" and createType != "finish":
                        mouseX = i.pos[0] * k_posX + 10 - int(i.pos[0] * k_posX+surfX) % 10
                        mouseY = i.pos[1] * k_posY + 10 - int(i.pos[1] * k_posY+surfY) % 10
                    else:
                        mouseX = i.pos[0] * k_posX
                        mouseY = i.pos[1] * k_posY
                else:
                    mouseX = i.pos[0] * k_posX
                    mouseY = i.pos[1] * k_posY
            if i.type == pygame.MOUSEBUTTONUP:
                if i.button == 1:
                    if gameMode == "creat":
                        if createType != "rollback" and createType != "spawnpoint" and createType != "bullets" and createType != "enemyFly" and createType != "finish":
                            map[createType][2].append(int(i.pos[0] * k_posX+surfX) + 10 - int(i.pos[0] * k_posX+surfX) % 10-(map[createType][0][-1]))
                            map[createType][3].append(int(i.pos[1] * k_posY+surfY) + 10 - int(i.pos[1] * k_posY+surfY) % 10-(map[createType][1][-1]))
                            if map[createType][2][-1] < 0:
                                map[createType][0][-1] = map[createType][0][-1] + map[createType][2][-1]
                                map[createType][2][-1] *= -1
                            if map[createType][3][-1] < 0:
                                map[createType][1][-1] = map[createType][1][-1] + map[createType][3][-1]
                                map[createType][3][-1] *= -1
                        else:
                            try:
                                map[createType][0].append(int(i.pos[0] * k_posX-map[createType][2]//2 + surfX))
                                map[createType][1].append(int(i.pos[1] * k_posY-map[createType][3]//2 + surfY))
                                if createType == "enemyFly":
                                    map[createType][-1].append(0)
                                    map[createType][4].append(0)
                                    map[createType][5].append(0)
                                    map[createType][6].append(False)
                                    map[createType][7][0].append(int(i.pos[0] * k_posX-map[createType][2]//2 + surfX))
                                    map[createType][7][1].append(int(i.pos[1] * k_posY-map[createType][3]//2 + surfY))
                                    map[createType][7][2].append(0)
                                    map[createType][7][3].append(0)
                                    map[createType][8].append(0)
                                    map[createType][9].append(hpEnemyFly)
                                elif createType == "bullets":
                                    map[createType][4].append(int(i.pos[0] * k_posX - map[createType][2] // 2 + surfX))
                                    map[createType][5].append(int(i.pos[1] * k_posY - map[createType][3] // 2 + surfY))
                            except:
                                map["bullets"] = [[], [], 15, 15, [], []]
                                map["enemyFly"] = [[], [], 21, 21, [], [], [], [[], [], [], []], [], [], []]
                                map["finish"] = [[], [], 24, 24]
                                map[createType][0].append(int(i.pos[0] * k_posX - map[createType][2] // 2 + surfX))
                                map[createType][1].append(int(i.pos[1] * k_posY - map[createType][3] // 2 + surfY))
                                if createType == "enemyFly":
                                    map[createType][-1].append(0)
                                    map[createType][4].append(0)
                                    map[createType][5].append(0)
                                    map[createType][6].append(False)
                                    map[createType][7][0].append(int(i.pos[0] * k_posX - map[createType][2]//2 + surfX))
                                    map[createType][7][1].append(int(i.pos[1] * k_posY - map[createType][3]//2 + surfY))
                                    map[createType][7][2].append(0)
                                    map[createType][7][3].append(0)
                                    map[createType][8].append(0)
                                    map[createType][9].append(hpEnemyFly)
                                elif createType == "bullets":
                                    map[createType][4].append(int(i.pos[0] * k_posX - map[createType][2] // 2 + surfX))
                                    map[createType][5].append(int(i.pos[1] * k_posY - map[createType][3] // 2 + surfY))
                            if createType == "rollback":
                                map[createType][4].append(0)
                        if createType == "background":
                            map[createType][4].append(createColor)
                        correctObject = {"block": [], "spikes": [], "spring": [], "rollback": [], "background": [],
                                         "spawnpoint": [], "bullets": [], "enemyFly": [], "finish": []}
                        correctObject[createType] = [-1]
                        draw = -1
                        print("\nmap =", map)
                elif i.button == 3:
                    if gameMode == "creat":
                        correctObject = {"block": [], "spikes": [], "spring": [], "rollback": [], "background": [],
                                         "spawnpoint": [], "bullets": [], "enemyFly": [], "finish": []}
                        if firstMouseX > mouseX:
                            mouseX = mouseX + firstMouseX
                            firstMouseX = mouseX - firstMouseX
                            mouseX = mouseX - firstMouseX
                        if firstMouseY > mouseY:
                            mouseY = mouseY + firstMouseY
                            firstMouseY = mouseY - firstMouseY
                            mouseY = mouseY - firstMouseY
                        for j in range(len(map["block"][3])):
                            if map["block"][0][j]+map["block"][2][j]-surfX > firstMouseX \
                                    and map["block"][0][j]-surfX < mouseX \
                                    and map["block"][1][j]+map["block"][3][j]-surfY > firstMouseY \
                                    and map["block"][1][j]-surfY < mouseY:
                                correctObject["block"].append(j)
                        for j in range(len(map["spikes"][3])):
                            if map["spikes"][0][j]+map["spikes"][2][j]-surfX > firstMouseX \
                                    and map["spikes"][0][j]-surfX < mouseX \
                                    and map["spikes"][1][j]+map["spikes"][3][j]-surfY > firstMouseY \
                                    and map["spikes"][1][j]-surfY < mouseY:
                                correctObject["spikes"].append(j)
                        for j in range(len(map["spring"][3])):
                            if map["spring"][0][j]+map["spring"][2][j]-surfX > firstMouseX \
                                    and map["spring"][0][j]-surfX < mouseX \
                                    and map["spring"][1][j]+map["spring"][3][j]-surfY > firstMouseY \
                                    and map["spring"][1][j]-surfY < mouseY:
                                correctObject["spring"].append(j)
                        for j in range(len(map["background"][3])):
                            if map["background"][0][j]+map["background"][2][j]-surfX > firstMouseX \
                                    and map["background"][0][j]-surfX < mouseX \
                                    and map["background"][1][j]+map["background"][3][j]-surfY > firstMouseY \
                                    and map["background"][1][j]-surfY < mouseY:
                                correctObject["background"].append(j)
                        for j in range(len(map["rollback"][4])):
                            if map["rollback"][0][j]+map["rollback"][2]-surfX > firstMouseX \
                                    and map["rollback"][0][j]-surfX < mouseX \
                                    and map["rollback"][1][j]+map["rollback"][3]-surfY > firstMouseY \
                                    and map["rollback"][1][j]-surfY < mouseY:
                                correctObject["rollback"].append(j)
                        for j in range(len(map["spawnpoint"][1])):
                            if map["spawnpoint"][0][j]+map["spawnpoint"][2]-surfX > firstMouseX \
                                    and map["spawnpoint"][0][j]-surfX < mouseX \
                                    and map["spawnpoint"][1][j]+map["spawnpoint"][3]-surfY > firstMouseY \
                                    and map["spawnpoint"][1][j]-surfY < mouseY:
                                correctObject["spawnpoint"].append(j)
                        try:
                            for j in range(len(map["bullets"][1])):
                                if map["bullets"][0][j]+map["bullets"][2]-surfX > firstMouseX \
                                        and map["bullets"][0][j]-surfX < mouseX \
                                        and map["bullets"][1][j]+map["bullets"][3]-surfY > firstMouseY \
                                        and map["bullets"][1][j]-surfY < mouseY:
                                    correctObject["bullets"].append(j)
                        except:
                            map["bullets"] = [[], [], 15, 15, [], []]
                        try:
                            for j in range(len(map["enemyFly"][1])):
                                if map["enemyFly"][0][j]+map["enemyFly"][2]-surfX > firstMouseX \
                                        and map["enemyFly"][0][j]-surfX < mouseX \
                                        and map["enemyFly"][1][j]+map["enemyFly"][3]-surfY > firstMouseY \
                                        and map["enemyFly"][1][j]-surfY < mouseY:
                                    correctObject["enemyFly"].append(j)
                        except:
                            map["enemyFly"] = [[], [], 21, 21, [], [], [], [[], [], [], []], [], [], []]
                        try:
                            for j in range(len(map["finish"][1])):
                                if map["finish"][0][j] + map["finish"][2] - surfX > firstMouseX \
                                        and map["finish"][0][j] - surfX < mouseX \
                                        and map["finish"][1][j] + map["finish"][3] - surfY > firstMouseY \
                                        and map["finish"][1][j] - surfY < mouseY:
                                    correctObject["finish"].append(j)
                        except:
                            map["finish"] = [[], [], 24, 24]
                        draw = -1
        for m in range(1):
            if gameMode == "surv" and victoryTime == 2 * FPS:
                if motionL == "stop" and motionR == "stop":
                    if speed > 0:
                        speed -= maxSpeed / 4
                    if speed <= 0:
                        speed = 0
                    if xO < x:
                        x += speed
                    elif xO > x:
                        x -= speed
                if dash == "stop":
                    if jump == "motion":
                        if speedJ-speedG > 0:
                            y -= speedJ
                        else:
                            jump = "stop"
                            speedJ = J
                            spring = 0
                            speedG = 0
                    elif jumpWallL == "motion":
                        if speedJ-speedG > 0:
                            y -= speedJ
                            if speedJ-speedG > speedJ//1.5:
                                stopRun = 1
                                x -= maxSpeed
                                speed = maxSpeed
                        else:
                            jumpWallL = "stop"
                            speedG = 0
                            speedJ = J
                            spring = 0
                    elif jumpWallR == "motion":
                        if speedJ-speedG > 0:
                            y -= speedJ
                            if speedJ-speedG > speedJ//1.5:
                                stopRun = 1
                                x += maxSpeed
                                speed = maxSpeed
                        else:
                            jumpWallR = "stop"
                            speedG = 0
                            speedJ = J
                            spring = 0
                    if motionL == "motion" and stopRun == 0:
                        if speed < maxSpeed:
                            speed += maxSpeed / 4
                        else:
                            speed = maxSpeed
                        x -= speed
                    if motionR == "motion" and stopRun == 0:
                        x += speed
                        if speed < maxSpeed:
                            speed += maxSpeed / 4
                        else:
                            speed = maxSpeed
                elif dash == "motion":
                    if timeDash < maxTimeDash:
                        timeDash += 1
                        grav = 0
                        speedG = 0
                        colorGG = PURPLE
                        colorGG2 = PURPLE2
                        x, y, speedG, speed = napravl(NDash, x, y, speedG, speed)
                    else:
                        if NDash != "down" and NDash != "downright" and NDash != "downleft":
                            grav = 0
                            speedG = 0
                            x, y, speedG, speed = napravl(NDash, x, y, speedG, speed)
                        dash = "stop"
                        grav = 1
                        timeDash = 0
                if shoot == "motion":
                    shoot = "stop"
                    speed //= 2
                    for i in range(-1, 2):
                        flyBullets[0].append(x + Size // 2)
                        flyBullets[1].append(y + Size // 2)
                        flyBullets[2].append(angle + 3 * i)
                        flyBullets[3].append(WHITE)
                if timeShoot > 0:
                    maxSpeed = 2
                    timeShoot -= 1
                    colorBullets = colorBullets2
                    if int((GunSec*FPS-timeShoot)//(GunSec*FPS//len(GUN))) < len(GUN):
                        Gun = GUN[int((GunSec*FPS-timeShoot)//(GunSec*FPS//len(GUN)))]
                else:
                    maxSpeed = 4
                    canShoot = True
                    Gun = GUN[0]
                    if bullets > 0:
                        colorBullets = colorBullets1
            elif gameMode == "creat":
                if motionL == "motion":
                    x -= 10
                elif motionR == "motion":
                    x += 10
                if motionU == "motion":
                    y -= 10
                elif motionD == "motion":
                    y += 10
            bulletDel = []
            for i in range(len(flyBullets[0])):
                sin = math.sin(math.radians(flyBullets[2][i]))
                cos = math.cos(math.radians(flyBullets[2][i]))
                flyBullets[0][i] += speedBullets * cos
                flyBullets[1][i] += speedBullets * sin
                if flyBullets[3][i][0] <= 50:
                    bulletDel.append(i)
                else:
                    flyBullets[3][i] = (flyBullets[3][i][0] - 12, flyBullets[3][i][1] - 12, flyBullets[3][i][2] - 12)
            bulletDel.sort(reverse=True)
            for flyBulDel in bulletDel:
                flyBullets[0].pop(flyBulDel)
                flyBullets[1].pop(flyBulDel)
                flyBullets[2].pop(flyBulDel)
                flyBullets[3].pop(flyBulDel)
        for G in range(1):
            if victoryTime < 2 * FPS:
                victoryTime -= 1
                if victoryTime == 0:
                    buttonMenu = ["Выход в главное меню", "Список карт"]
                    menu = "menu"
                    pygame.mixer.music.unpause()
                    pygame.mixer.music.set_volume(0.15)
            if gameMode == "surv" and victoryTime == 2 * FPS:
                if grav == 1:
                    canJump = False
                    canJumpWallL = False
                    canJumpWallR = False
                    y += speedG
                    if speedG < speedJ:
                        speedG += g
                if y >= minY-Size:
                    y = minY-Size
                    grav = 0
                    speedG = 0
                    timeCoyoteL = 5
                    timeCoyoteR = 5
                    canJump = True
                    canDash = True
                    canJumpWallL = False
                    canJumpWallR = False
                    if y > minY - Size:
                        dash = "stop"
                        timeDash = 0
                bulFlex = []
                for bul in range(len(flyBullets[0])):
                    sin = math.sin(math.radians(flyBullets[2][bul]))
                    cos = math.cos(math.radians(flyBullets[2][bul]))
                    if flyBullets[1][bul] > minY:
                        bulFlex.append(bul)
                        hitWallSound.play()
                bulFlex.sort(reverse=True)
                for bulFlexDel in bulFlex:
                    flyBullets[0].pop(bulFlexDel)
                    flyBullets[1].pop(bulFlexDel)
                    flyBullets[2].pop(bulFlexDel)
                    flyBullets[3].pop(bulFlexDel)
                try:
                    for enem in range(len(map["enemyFly"][1])):
                        if map["enemyFly"][9][enem] <= 0:
                            continue
                        if map["enemyFly"][1][enem] >= minY - map["enemyFly"][2]:
                            map["enemyFly"][1][enem] = minY - map["enemyFly"][2]
                except:
                    pass
                FlagWall = False
                if len(map["block"][0]) == 0:
                    try:
                        for enem in range(len(map["enemyFly"][1])):
                            if map["enemyFly"][9][enem] <= 0:
                                continue
                            if (((x - map["enemyFly"][0][enem]) ** 2 + (y - map["enemyFly"][1][enem]) ** 2) ** 0.5 <= lengthSmell) \
                                    or (((x - map["enemyFly"][0][enem]) ** 2 + (y - map["enemyFly"][1][enem]) ** 2) ** 0.5 <= lengthFallSmell \
                                    and map["enemyFly"][8][enem] > 0):
                                map["enemyFly"][4][enem] = x
                                map["enemyFly"][5][enem] = y
                                if map["enemyFly"][6][enem] == False:
                                    map["enemyFly"][6][enem] = True
                                    if map["enemyFly"][8][enem] == 0:
                                        map["enemyFly"][8][enem] = timerStan
                                        startEnemyFlySound.play()
                            else:
                                if map["enemyFly"][6][enem]:
                                    map["enemyFly"][6][enem] = False
                    except:
                        pass
                else:
                    for i in range(len(map["block"][0])):
                        bulFlex = []
                        for bul in range(len(flyBullets[0])):
                            sin = math.sin(math.radians(flyBullets[2][bul]))
                            cos = math.cos(math.radians(flyBullets[2][bul]))
                            for hit in range(3):
                                hitLen = lengthBullets // 2 * hit
                                if flyBullets[1][bul] - hitLen * sin >= map["block"][1][i] and flyBullets[1][bul] - hitLen * sin < map["block"][1][i] + map["block"][3][i] \
                                        and flyBullets[0][bul] - hitLen * cos > map["block"][0][i] and flyBullets[0][bul] - hitLen * cos < map["block"][0][i] + map["block"][2][i]:
                                    bulFlex.append(bul)
                                    hitWallSound.play()
                                    break
                        bulFlex.sort(reverse=True)
                        for bulFlexDel in bulFlex:
                            flyBullets[0].pop(bulFlexDel)
                            flyBullets[1].pop(bulFlexDel)
                            flyBullets[2].pop(bulFlexDel)
                            flyBullets[3].pop(bulFlexDel)
                        try:
                            for enem in range(len(map["enemyFly"][1])):
                                if map["enemyFly"][9][enem] <= 0:
                                    continue
                                if map["enemyFly"][1][enem] + map["enemyFly"][3] > map["block"][1][i] - helpEnemy and \
                                        map["enemyFly"][1][enem] < map["block"][1][i] + map["block"][3][i] + helpEnemy \
                                        and map["enemyFly"][0][enem] + map["enemyFly"][2] > map["block"][0][i] - helpEnemy and \
                                        map["enemyFly"][0][enem] < map["block"][0][i] + map["block"][2][i] + helpEnemy:
                                    if math.fabs((map["enemyFly"][1][enem] + map["enemyFly"][3] // 2) - map["block"][1][
                                        i]) < math.fabs((map["enemyFly"][1][enem] + map["enemyFly"][3] // 2) - (
                                            map["block"][1][i] + map["block"][3][i])) \
                                            and math.fabs(
                                        (map["enemyFly"][1][enem] + map["enemyFly"][3] // 2) - map["block"][1][
                                            i]) < math.fabs((map["enemyFly"][0][enem] + map["enemyFly"][2] // 2) - (
                                            map["block"][0][i] + map["block"][2][i])) \
                                            and math.fabs(
                                        (map["enemyFly"][1][enem] + map["enemyFly"][3] // 2) - map["block"][1][
                                            i]) < math.fabs(
                                        (map["enemyFly"][0][enem] + map["enemyFly"][2] // 2) - (map["block"][0][i])):
                                        map["enemyFly"][1][enem] = map["block"][1][i] - map["enemyFly"][3]
                                        if map["enemyFly"][6][enem] == False:
                                            map["enemyFly"][4][enem] = map["enemyFly"][0][enem]
                                            map["enemyFly"][5][enem] = map["enemyFly"][1][enem]
                                    elif math.fabs((map["enemyFly"][1][enem] + map["enemyFly"][3] // 2) - (
                                            map["block"][1][i] + map["block"][3][i])) < math.fabs(
                                        (map["enemyFly"][1][enem] + map["enemyFly"][3] // 2) - map["block"][1][i]) \
                                            and math.fabs((map["enemyFly"][1][enem] + map["enemyFly"][3] // 2) - (
                                            map["block"][1][i] + map["block"][3][i])) < math.fabs(
                                        (map["enemyFly"][0][enem] + map["enemyFly"][2] // 2) - (
                                                map["block"][0][i] + map["block"][2][i])) \
                                            and math.fabs((map["enemyFly"][1][enem] + map["enemyFly"][3] // 2) - (
                                            map["block"][1][i] + map["block"][3][i])) < math.fabs(
                                        (map["enemyFly"][0][enem] + map["enemyFly"][2] // 2) - (map["block"][0][i])):
                                        map["enemyFly"][1][enem] = map["block"][1][i] + map["block"][3][i]
                                        if map["enemyFly"][6][enem] == False:
                                            map["enemyFly"][4][enem] = map["enemyFly"][0][enem]
                                            map["enemyFly"][5][enem] = map["enemyFly"][1][enem]
                                    elif math.fabs((map["enemyFly"][0][enem] + map["enemyFly"][2] // 2) - (
                                            map["block"][0][i] + map["block"][2][i])) < math.fabs(
                                        (map["enemyFly"][1][enem] + map["enemyFly"][3] // 2) - map["block"][1][i]) \
                                            and math.fabs((map["enemyFly"][0][enem] + map["enemyFly"][2] // 2) - (
                                            map["block"][0][i] + map["block"][2][i])) < math.fabs(
                                        (map["enemyFly"][1][enem] + map["enemyFly"][3] // 2) - (
                                                map["block"][1][i] + map["block"][3][i])) \
                                            and math.fabs((map["enemyFly"][0][enem] + map["enemyFly"][2] // 2) - (
                                            map["block"][0][i] + map["block"][2][i])) < math.fabs(
                                        (map["enemyFly"][0][enem] + map["enemyFly"][2] // 2) - (map["block"][0][i])):
                                        map["enemyFly"][0][enem] = map["block"][0][i] + map["block"][2][i]
                                        if map["enemyFly"][6][enem] == False:
                                            map["enemyFly"][4][enem] = map["enemyFly"][0][enem]
                                            map["enemyFly"][5][enem] = map["enemyFly"][1][enem]
                                    elif math.fabs((map["enemyFly"][0][enem] + map["enemyFly"][2] // 2) - (
                                            map["block"][0][i])) < math.fabs(
                                        (map["enemyFly"][1][enem] + map["enemyFly"][3] // 2) - map["block"][1][i]) \
                                            and math.fabs((map["enemyFly"][0][enem] + map["enemyFly"][2] // 2) - (
                                            map["block"][0][i])) < math.fabs(
                                        (map["enemyFly"][0][enem] + map["enemyFly"][2] // 2) - (
                                                map["block"][0][i] + map["block"][2][i])) \
                                            and math.fabs((map["enemyFly"][0][enem] + map["enemyFly"][2] // 2) - (
                                            map["block"][0][i])) < math.fabs(
                                        (map["enemyFly"][1][enem] + map["enemyFly"][3] // 2) - (
                                                map["block"][1][i] + map["block"][3][i])):
                                        map["enemyFly"][0][enem] = map["block"][0][i] - map["enemyFly"][2]
                                        if map["enemyFly"][6][enem] == False:
                                            map["enemyFly"][4][enem] = map["enemyFly"][0][enem]
                                            map["enemyFly"][5][enem] = map["enemyFly"][1][enem]
                        except:
                            pass
                        if y+Size >= map["block"][1][i] and y < map["block"][1][i]+map["block"][3][i] \
                                and x+Size > map["block"][0][i] and x < map["block"][0][i]+map["block"][2][i] and yO <= y \
                                and xO+Size > map["block"][0][i] and xO < map["block"][0][i]+map["block"][2][i]:
                            speedJ = J
                            y = map["block"][1][i]-Size
                            grav = 0
                            speedG = 0
                            canJump = True
                            canDash = True
                            canJumpWallL = False
                            canJumpWallR = False
                            timeCoyoteL = 5
                            timeCoyoteR = 5
                            if y + Size > map["block"][1][i]:
                                dash = "stop"
                                timeDash = 0
                        elif y+Size > map["block"][1][i] and y < map["block"][1][i]+map["block"][3][i] \
                                and x+Size > map["block"][0][i] and x < map["block"][0][i]+map["block"][2][i] and yO > y \
                                and xO+Size > map["block"][0][i] and xO < map["block"][0][i]+map["block"][2][i]:
                            jump = "stop"
                            speedJ = J
                            jumpWallL = "stop"
                            jumpWallR = "stop"
                            y = map["block"][1][i]+map["block"][3][i]
                            speedG = 0
                            dash = "stop"
                            timeDash = 0
                            canJumpWallL = False
                            canJumpWallR = False
                        if x+Size > map["block"][0][i] and x < map["block"][0][i]+map["block"][2][i] \
                                and y+Size > map["block"][1][i] and y < map["block"][1][i]+map["block"][3][i] and xO < x \
                                and yO+Size > map["block"][1][i] and yO < map["block"][1][i]+map["block"][3][i]:
                            x = map["block"][0][i]-Size
                            speed = 0.1
                            dash = "stop"
                            speedJ = J
                            timeDash = 0
                            canJumpWallL = True
                            timeCoyoteL = 0
                            jumpWallL = "stop"
                            FlagWall = True
                            if jump == 'stop' and jumpWallR == "stop" and jumpWallL == "stop":
                                speedG = 2
                        elif x+Size > map["block"][0][i] and x < map["block"][0][i]+map["block"][2][i] \
                                and y+Size > map["block"][1][i] and y < map["block"][1][i]+map["block"][3][i] and xO > x \
                                and yO+Size > map["block"][1][i] and yO < map["block"][1][i]+map["block"][3][i]:
                            x = map["block"][0][i]+map["block"][2][i]
                            speed = 0.1
                            dash = "stop"
                            speedJ = J
                            timeDash = 0
                            canJumpWallR = True
                            timeCoyoteR = 0
                            jumpWallR = "stop"
                            FlagWall = True
                            if jump == 'stop' and jumpWallR == "stop" and jumpWallL == "stop":
                                speedG = 2
                        if x + Size + 6 > map["block"][0][i] and x < map["block"][0][i] + map["block"][2][i] \
                                and y + Size > map["block"][1][i] and y < map["block"][1][i] + map["block"][3][i] and xO <= x \
                                and yO + Size > map["block"][1][i] and yO < map["block"][1][i] + map["block"][3][i]:
                            if canJump == False:
                                canJumpWallL = True
                        elif x + Size > map["block"][0][i] and x - 6 < map["block"][0][i] + map["block"][2][i] \
                                and y + Size > map["block"][1][i] and y < map["block"][1][i] + map["block"][3][i] and xO >= x \
                                and yO + Size > map["block"][1][i] and yO < map["block"][1][i] + map["block"][3][i]:
                            if canJump == False:
                                canJumpWallR = True
                    try:
                        for enem in range(len(map["enemyFly"][1])):
                            if map["enemyFly"][9][enem] <= 0:
                                continue
                            lengthEnemyTrue = ((x - map["enemyFly"][0][enem]) ** 2 + (
                                    y - map["enemyFly"][1][enem]) ** 2) ** 0.5
                            try:
                                sin = (y - map["enemyFly"][1][enem]) / lengthEnemyTrue
                                cos = (x - map["enemyFly"][0][enem]) / lengthEnemyTrue
                            except:
                                sin = 0
                                cos = 0
                            if (lengthEnemyTrue <= lengthSmell) \
                                    or (lengthEnemyTrue <= lengthFallSmell and map["enemyFly"][8][enem] > 0):
                                FWallEnemy = True
                                for i in range(len(map["block"][0])):
                                    if lengthEnemyTrue < 10:
                                        map["enemyFly"][4][enem] = x
                                        map["enemyFly"][5][enem] = y
                                        if map["enemyFly"][6][enem] == False:
                                            map["enemyFly"][6][enem] = True
                                            if map["enemyFly"][8][enem] == 0:
                                                map["enemyFly"][8][enem] = timerStan
                                                startEnemyFlySound.play()
                                            break
                                    else:
                                        for doble in range(2):
                                            if (map["enemyFly"][0][enem] - x) * (map["enemyFly"][1][enem] - y) > 0:
                                                xFoundWall = map["enemyFly"][0][enem] + map["enemyFly"][2] * doble
                                                yFoundWall = map["enemyFly"][1][enem] + map["enemyFly"][3] * (1 - doble)
                                            else:
                                                xFoundWall = map["enemyFly"][0][enem] + map["enemyFly"][2] * doble
                                                yFoundWall = map["enemyFly"][1][enem] + map["enemyFly"][3] * doble
                                            for ii in range(0, int(lengthEnemyTrue // 5)):
                                                xFoundWall += 5 * cos
                                                yFoundWall += 5 * sin
                                                if yFoundWall > map["block"][1][i] \
                                                        and yFoundWall < map["block"][1][i] + map["block"][3][i] \
                                                        and xFoundWall > map["block"][0][i] \
                                                        and xFoundWall < map["block"][0][i] + map["block"][2][i]:
                                                    FWallEnemy = False
                                                    break
                                            if FWallEnemy == False:
                                                break
                                        if FWallEnemy == False:
                                            break
                                if FWallEnemy:
                                    map["enemyFly"][4][enem] = x
                                    map["enemyFly"][5][enem] = y
                                    if map["enemyFly"][6][enem] == False:
                                        map["enemyFly"][6][enem] = True
                                        if map["enemyFly"][8][enem] == 0:
                                            map["enemyFly"][8][enem] = timerStan
                                            startEnemyFlySound.play()
                                else:
                                    if map["enemyFly"][6][enem]:
                                        map["enemyFly"][6][enem] = False
                            else:
                                if map["enemyFly"][6][enem]:
                                    map["enemyFly"][6][enem] = False
                    except:
                        pass
                try:
                    for enem in range(len(map["enemyFly"][1])):
                        if map["enemyFly"][9][enem] <= 0:
                            continue
                        bulFlex = []
                        for bul in range(len(flyBullets[0])):
                            sin = math.sin(math.radians(flyBullets[2][bul]))
                            cos = math.cos(math.radians(flyBullets[2][bul]))
                            for hit in range(3):
                                hitLen = lengthBullets // 2 * hit
                                if flyBullets[1][bul] - hitLen * sin >= map["enemyFly"][1][enem] \
                                        and flyBullets[1][bul] - hitLen * sin < map["enemyFly"][1][enem] + map["enemyFly"][3] \
                                        and flyBullets[0][bul] - hitLen * cos > map["enemyFly"][0][enem] \
                                        and flyBullets[0][bul] - hitLen * cos < map["enemyFly"][0][enem] + map["enemyFly"][2]:
                                    bulFlex.append(bul)
                                    hitEnemSound.play()
                                    map["enemyFly"][7][2][enem] = (flyBullets[2][bul] + map["enemyFly"][7][2][enem]) / 2
                                    map["enemyFly"][7][3][enem] += speedBullets // 6
                                    map["enemyFly"][6][enem] = True
                                    map["enemyFly"][8][enem] = timerStan
                                    map["enemyFly"][4][enem] = x
                                    map["enemyFly"][5][enem] = y
                                    map["enemyFly"][9][enem] -= damage
                                    if map["enemyFly"][9][enem] <= 0:
                                        dieEnemySound.play()
                                    break
                        bulFlex.sort(reverse=True)
                        for bulFlexDel in bulFlex:
                            flyBullets[0].pop(bulFlexDel)
                            flyBullets[1].pop(bulFlexDel)
                            flyBullets[2].pop(bulFlexDel)
                            flyBullets[3].pop(bulFlexDel)
                        if map["enemyFly"][7][3][enem] > 0:
                            sin = math.sin(math.radians(map["enemyFly"][7][2][enem]))
                            cos = math.cos(math.radians(map["enemyFly"][7][2][enem]))
                            map["enemyFly"][0][enem] += map["enemyFly"][7][3][enem] * cos
                            map["enemyFly"][1][enem] += map["enemyFly"][7][3][enem] * sin
                            map["enemyFly"][7][3][enem] -= map["enemyFly"][7][3][enem] / 10
                        else:
                            map["enemyFly"][7][2][enem] = 0
                            map["enemyFly"][7][3][enem] = 0
                except:
                    pass
                if FlagWall:
                    if playSoundSlide == 1:
                        runSound.play(-1)
                        playSoundSlide = 0
                else:
                    if playSoundSlide == 0:
                        runSound.stop()
                        playSoundSlide = 1
                for i in range(len(map["spikes"][0])):
                    bulFlex = []
                    for bul in range(len(flyBullets[0])):
                        sin = math.sin(math.radians(flyBullets[2][bul]))
                        cos = math.cos(math.radians(flyBullets[2][bul]))
                        for hit in range(3):
                            hitLen = lengthBullets // 2 * hit
                            if flyBullets[1][bul] - hitLen * sin >= map["spikes"][1][i] and flyBullets[1][
                                bul] - hitLen * sin < map["spikes"][1][i] + map["spikes"][3][i] \
                                    and flyBullets[0][bul] - hitLen * cos > map["spikes"][0][i] and flyBullets[0][
                                bul] - hitLen * cos < map["spikes"][0][i] + map["spikes"][2][i]:
                                bulFlex.append(bul)
                                hitWallSound.play()
                                break
                    bulFlex.sort(reverse=True)
                    for bulFlexDel in bulFlex:
                        flyBullets[0].pop(bulFlexDel)
                        flyBullets[1].pop(bulFlexDel)
                        flyBullets[2].pop(bulFlexDel)
                        flyBullets[3].pop(bulFlexDel)
                    if y + Size > map["spikes"][1][i]+5 and y < map["spikes"][1][i] + map["spikes"][3][i]-5 \
                    and x + Size > map["spikes"][0][i]+5 and x < map["spikes"][0][i] + map["spikes"][2][i]-5:
                        if canCreate == False:
                            add_death()
                        dieSound.play()
                        x = spawnX
                        y = spawnY
                        xO = x
                        yO = y
                        surfX = spawnSX
                        surfY = spawnSY
                        motionL = 'stop'
                        motionR = 'stop'
                        motionU = 'stop'
                        motionD = 'stop'
                        dash = 'stop'
                        jump = 'stop'
                        jumpWallL = "stop"
                        jumpWallR = "stop"
                        speed = 0
                        speedG = 0
                        timeDash = 0
                        canJump = False
                        canJumpWallR = False
                        canJumpWallL = False
                        canDash = False
                        for j in range(len(map["rollback"][4])):
                            map["rollback"][4][j] = 0
                        if "enemyFly" in map:
                            for ret in range(len(map["enemyFly"][0])):
                                if map["enemyFly"][9][ret] > 0:
                                    map["enemyFly"][-1][ret] = 0
                                    map["enemyFly"][4][ret] = 0
                                    map["enemyFly"][5][ret] = 0
                                    map["enemyFly"][6][ret] = False
                                    map["enemyFly"][0][ret] = map["enemyFly"][7][0][ret]
                                    map["enemyFly"][1][ret] = map["enemyFly"][7][1][ret]
                                    map["enemyFly"][7][2][ret] = 0
                                    map["enemyFly"][7][3][ret] = 0
                                    map["enemyFly"][8][ret] = 0
                for i in range(len(map["spring"][0])):
                    bulFlex = []
                    for bul in range(len(flyBullets[0])):
                        sin = math.sin(math.radians(flyBullets[2][bul]))
                        cos = math.cos(math.radians(flyBullets[2][bul]))
                        for hit in range(3):
                            hitLen = lengthBullets // 2 * hit
                            if flyBullets[1][bul] - hitLen * sin >= map["spring"][1][i] and flyBullets[1][
                                bul] - hitLen * sin < map["spring"][1][i] + map["spring"][3][i] \
                                    and flyBullets[0][bul] - hitLen * cos > map["spring"][0][i] and flyBullets[0][
                                bul] - hitLen * cos < map["spring"][0][i] + map["spring"][2][i]:
                                bulFlex.append(bul)
                                break
                    bulFlex.sort(reverse=True)
                    for bulFlexDel in bulFlex:
                        flyBullets[0].pop(bulFlexDel)
                        flyBullets[1].pop(bulFlexDel)
                        flyBullets[2].pop(bulFlexDel)
                        flyBullets[3].pop(bulFlexDel)
                    if y + Size > map["spring"][1][i] and y < map["spring"][1][i] + map["spring"][3][i] \
                    and x + Size > map["spring"][0][i] and x < map["spring"][0][i] + map["spring"][2][i]:
                        spring = 1
                        speedJ = SpringJ
                        jump = "motion"
                        dash = "stop"
                        timeDash = 0
                        grav = 0
                        speedG = 0
                        canDash = True
                        canJumpWallL = False
                        canJumpWallR = False
                        canJump = False
                for i in range(len(map["rollback"][0])):
                    if y + Size > map["rollback"][1][i]-2 and y < map["rollback"][1][i] + map["rollback"][3]+2 \
                            and x + Size > map["rollback"][0][i]-2 and x < map["rollback"][0][i] + map["rollback"][2]+2:
                        if canDash == False and map["rollback"][4][i] == 0:
                            canDash = True
                            rollbackSound.play()
                            map["rollback"][4][i] += 1
                    if map["rollback"][4][i] > 0:
                        map["rollback"][4][i] += 1
                    if map["rollback"][4][i] >= timeRollback:
                        map["rollback"][4][i] = 0
                for i in range(len(map["spawnpoint"][0])):
                    if y + Size > map["spawnpoint"][1][i] and y < map["spawnpoint"][1][i] + map["spawnpoint"][3] \
                            and x + Size > map["spawnpoint"][0][i] and x < map["spawnpoint"][0][i] + map["spawnpoint"][2]:
                        spawnX = map["spawnpoint"][0][i]
                        spawnY = map["spawnpoint"][1][i]
                        if spawnSX != spawnX - 440 or spawnSY != spawnY - 250:
                            saveSound.play()
                        spawnSX = spawnX - 440
                        spawnSY = spawnY - 250
                        map["spawnpoint"][4] = i
                try:
                    for i in range(len(map["finish"][0])):
                        if y + Size > map["finish"][1][i] and y < map["finish"][1][i] + map["finish"][3] \
                                and x + Size > map["finish"][0][i] and x < map["finish"][0][i] + map["finish"][2]:
                            if canCreate == False:
                                if victoryTime == 2 * FPS:
                                    win = finish_level()
                                    finishSound.play()
                                    victoryTime -= 1
                except:
                    pass
                try:
                    if bullets < bulletsMax:
                        for i in range(len(map["bullets"][0])):
                            if y + Size > map["bullets"][1][i] and y < map["bullets"][1][i] + map["bullets"][3] \
                                    and x + Size > map["bullets"][0][i] and x < map["bullets"][0][i] + map["bullets"][2]\
                                    and bullets < bulletsMax:
                                bullets += min(3, bulletsMax-bullets)
                                chargerSound.play()
                                map["bullets"][1][i] = 3000
                except:
                    pass
                try:
                    if (True in map["enemyFly"][6]) or (sum(map["enemyFly"][8]) > 0):
                        for enem in range(len(map["enemyFly"][1])):
                            if map["enemyFly"][9][enem] <= 0:
                                continue
                            if map["enemyFly"][6][enem]:
                                try:
                                    sin = (y - map["enemyFly"][1][enem]) / ((y - map["enemyFly"][1][enem])**2 + (
                                            x - map["enemyFly"][0][enem])**2)**0.5
                                    cos = (x - map["enemyFly"][0][enem]) / ((y - map["enemyFly"][1][enem]) ** 2 + (
                                                x - map["enemyFly"][0][enem]) ** 2) ** 0.5
                                except:
                                    sin = 0
                                    cos = 0
                                map["enemyFly"][0][enem] += speedEnemy * cos
                                map["enemyFly"][1][enem] += speedEnemy * sin
                            elif (map["enemyFly"][0][enem] != map["enemyFly"][4][enem] \
                                or map["enemyFly"][1][enem] != map["enemyFly"][5][enem]):
                                oldLengthEnem = ((map["enemyFly"][1][enem] - map["enemyFly"][5][enem]) ** 2 + (map["enemyFly"][0][enem] - map["enemyFly"][4][enem]) ** 2) ** 0.5
                                if (oldLengthEnem > 0 and oldLengthEnem < speedEnemy) and map["enemyFly"][8][enem] > 0:
                                    map["enemyFly"][0][enem] = map["enemyFly"][4][enem]
                                    map["enemyFly"][1][enem] = map["enemyFly"][5][enem]
                                elif oldLengthEnem >= speedEnemy and map["enemyFly"][8][enem] > 0:
                                    try:
                                        sin = (map["enemyFly"][5][enem] - map["enemyFly"][1][enem]) / oldLengthEnem
                                        cos = (map["enemyFly"][4][enem] - map["enemyFly"][0][enem]) / oldLengthEnem
                                    except:
                                        sin = 0
                                        cos = 0
                                    map["enemyFly"][0][enem] += speedEnemy * cos
                                    map["enemyFly"][1][enem] += speedEnemy * sin
                            elif map["enemyFly"][8][enem] > 0:
                                map["enemyFly"][8][enem] -= 1
                                if map["enemyFly"][8][enem] == 0:
                                    stopEnemyFlySound.play()
                            if y + Size > map["enemyFly"][1][enem] and y < map["enemyFly"][1][enem] + map["enemyFly"][3] \
                                    and x + Size > map["enemyFly"][0][enem] and x < map["enemyFly"][0][enem] + map["enemyFly"][2]:
                                if canCreate == False:
                                    add_death()
                                dieSound.play()
                                x = spawnX
                                y = spawnY
                                xO = x
                                yO = y
                                surfX = spawnSX
                                surfY = spawnSY
                                motionL = 'stop'
                                motionR = 'stop'
                                motionU = 'stop'
                                motionD = 'stop'
                                dash = 'stop'
                                jump = 'stop'
                                jumpWallL = "stop"
                                jumpWallR = "stop"
                                speed = 0
                                speedG = 0
                                timeDash = 0
                                canJump = False
                                canJumpWallR = False
                                canJumpWallL = False
                                canDash = False
                                for j in range(len(map["rollback"][4])):
                                    map["rollback"][4][j] = 0
                                if "enemyFly" in map:
                                    for ret in range(len(map["enemyFly"][0])):
                                        if map["enemyFly"][9][ret] > 0:
                                            map["enemyFly"][-1][ret] = 0
                                            map["enemyFly"][4][ret] = 0
                                            map["enemyFly"][5][ret] = 0
                                            map["enemyFly"][6][ret] = False
                                            map["enemyFly"][0][ret] = map["enemyFly"][7][0][ret]
                                            map["enemyFly"][1][ret] = map["enemyFly"][7][1][ret]
                                            map["enemyFly"][7][2][ret] = 0
                                            map["enemyFly"][7][3][ret] = 0
                                            map["enemyFly"][8][ret] = 0
                except:
                    pass
                if timeCoyoteL < 5:
                    timeCoyoteL += 1
                    canJumpWallL = True
                if timeCoyoteR < 5:
                    timeCoyoteR += 1
                    canJumpWallR = True
        for e in range(1):
            if x < surfX+(WIDTH-surf)//2:
                surfX -= speedSX
                if speedSX < maxSpeed:
                    speedSX += surfG
                else:
                    speedSX = maxSpeed
                if surfX+(WIDTH-surf)//2-x >= Size * 1.3:
                    speedSX = abs(xO - x)
            elif x+Size > surfX+(WIDTH+surf)//2:
                surfX += speedSX
                if speedSX < maxSpeed:
                    speedSX += surfG
                else:
                    speedSX = maxSpeed
                if x+Size-(surfX+(WIDTH+surf)//2) >= Size * 1.3:
                    speedSX = abs(xO - x)
            else:
                speedSX = 0
            if y < surfY+(HEIGHT-surf)//2:
                if speedSY < speedJ-speedG:
                    if jump == "motion" or dash == "motion":
                        speedSY += surfG
                else:
                    if jump == "motion" or dash == "motion":
                        speedSY = speedJ-speedG
                if surfY+(HEIGHT-surf)//2-y > Size * 1.3:
                    speedSY = abs(yO - y)
                surfY -= speedSY
            elif y+Size > surfY+(HEIGHT+surf)//2:
                if speedSY < speedG:
                    speedSY += g
                else:
                    if speedG != 0:
                        speedSY = speedG
                if y+Size-surfY-(HEIGHT+surf)//2 > Size * 1.3:
                    speedSY = abs(yO - y)
                surfY += speedSY
            else:
                speedSY = 0
            TrueX = x-surfX
            TrueY = y-surfY
        for d in range(1):
            for i in range(len(map["background"][3])):
                if map["background"][0][i] + map["background"][2][i] > surfX and map["background"][1][i] + map["background"][3][i] > surfY \
                        and map["background"][0][i] < surfX + WIDTH and map["background"][1][i] < surfY + HEIGHT:
                    pygame.draw.rect(screen, map["background"][4][i], (map["background"][0][i]-surfX, map["background"][1][i]-surfY, map["background"][2][i],
                                                     map["background"][3][i]))
            try:
                for i in range(len(map["enemyFly"][1])):
                    if map["enemyFly"][9][i] <= 0:
                        if map["enemyFly"][0][i] + map["enemyFly"][2] > surfX \
                                and map["enemyFly"][1][i] + map["enemyFly"][3] > surfY \
                                and map["enemyFly"][0][i] < surfX + WIDTH and map["enemyFly"][1][i] < surfY + HEIGHT:
                            enemyFly = ENEMYDIE1
                            for j in range(len(enemyFly[0])):
                                drawX = map["enemyFly"][0][i] + enemyFly[0][j] - surfX
                                drawY = map["enemyFly"][1][i] + enemyFly[1][j] - surfY
                                pygame.draw.rect(screen, enemyFly[2][j], (drawX, drawY, 3, 3))
            except:
                pass
            timeCadrRoll += 1
            if timeCadrRoll >= FPS * RollBackSec // len(RollBackTexture):
                if cadrRoll + 1 < len(RollBackTexture):
                    cadrRoll += 1
                else:
                    cadrRoll = 0
                timeCadrRoll = 0
            RollTex = RollBackTexture[cadrRoll]
            RollTex2 = RollBackTexture2[cadrRoll]
            for i in range(len(map["rollback"][4])):
                if map["rollback"][0][i] + map["rollback"][2] > surfX \
                        and map["rollback"][1][i] + map["rollback"][3] > surfY \
                        and map["rollback"][0][i] < surfX + WIDTH and map["rollback"][1][i] < surfY + HEIGHT:
                    if map["rollback"][4][i] == 0:
                        for j in range(len(RollTex[0])):
                            drawX = map["rollback"][0][i] + RollTex[0][j] - surfX
                            drawY = map["rollback"][1][i] + RollTex[1][j] - surfY
                            pygame.draw.rect(screen, RollTex[2][j], (drawX, drawY, 2, 2))
                    else:
                        for j in range(len(RollTex2[0])):
                            drawX = map["rollback"][0][i] + RollTex2[0][j] - surfX
                            drawY = map["rollback"][1][i] + RollTex2[1][j] - surfY
                            pygame.draw.rect(screen, RollTex2[2][j], (drawX, drawY, 2, 2))
            timeCadrSpawn += 1
            timeCadrSpawn2 += 1
            if timeCadrSpawn >= FPS * SpawnSec // len(SpawnTexture):
                if cadrSpawn + 1 < len(SpawnTexture):
                    cadrSpawn += 1
                else:
                    cadrSpawn = 0
                timeCadrSpawn = 0
            if timeCadrSpawn2 >= FPS * SpawnSec2 // len(SpawnTexture2):
                if cadrSpawn2 + 1 < len(SpawnTexture2):
                    cadrSpawn2 += 1
                else:
                    cadrSpawn2 = 0
                timeCadrSpawn2 = 0
            SpawnTex = SpawnTexture[cadrSpawn]
            SpawnTex2 = SpawnTexture2[cadrSpawn2]
            for i in range(len(map["spawnpoint"][1])):
                if map["spawnpoint"][0][i] + map["spawnpoint"][2] > surfX \
                        and map["spawnpoint"][1][i] + map["spawnpoint"][3] > surfY \
                        and map["spawnpoint"][0][i] < surfX + WIDTH and map["spawnpoint"][1][i] < surfY + HEIGHT:
                    if map["spawnpoint"][-1] == i:
                        for j in range(len(SpawnTex2[0])):
                            drawX = map["spawnpoint"][0][i] + SpawnTex2[0][j] - surfX
                            drawY = map["spawnpoint"][1][i] + SpawnTex2[1][j] - surfY
                            pygame.draw.rect(screen, SpawnTex2[2][j], (drawX, drawY, 3, 3))
                    else:
                        for j in range(len(SpawnTex[0])):
                            drawX = map["spawnpoint"][0][i] + SpawnTex[0][j] - surfX
                            drawY = map["spawnpoint"][1][i] + SpawnTex[1][j] - surfY
                            pygame.draw.rect(screen, SpawnTex[2][j], (drawX, drawY, 3, 3))
            if finishTimeCadr < finishSec * FPS:
                finishTimeCadr += 1
                if finishTimeCadr >= finishSec * FPS:
                    finishTimeCadr = 0
            finishTex = FINISH[min(int(finishTimeCadr // (finishSec*FPS/len(FINISH))), len(FINISH) - 1)]
            try:
                for i in range(len(map["finish"][0])):
                    if map["finish"][0][i] + map["finish"][2] > surfX \
                            and map["finish"][1][i] + map["finish"][3] > surfY \
                            and map["finish"][0][i] < surfX + WIDTH and map["finish"][1][i] < surfY + HEIGHT:
                        for j in range(len(finishTex[0])):
                            drawX = map["finish"][0][i] + finishTex[0][j] - surfX
                            drawY = map["finish"][1][i] + finishTex[1][j] - surfY
                            pygame.draw.rect(screen, finishTex[2][j], (drawX, drawY, 3, 3))
            except:
                pass
            try:
                for i in range(len(map["bullets"][1])):
                    if map["bullets"][0][i] + map["bullets"][2] > surfX \
                            and map["bullets"][1][i] + map["bullets"][3] > surfY \
                            and map["bullets"][0][i] < surfX + WIDTH and map["bullets"][1][i] < surfY + HEIGHT:
                        for j in range(len(BulletTexture[0])):
                            drawX = map["bullets"][0][i] + BulletTexture[0][j] - surfX
                            drawY = map["bullets"][1][i] + BulletTexture[1][j] - surfY
                            pygame.draw.rect(screen, BulletTexture[2][j], (drawX, drawY, 3, 3))
            except:
                pass
            for i in range(len(flyBullets[0])):
                if flyBullets[0][i] + lengthBullets * cos > surfX \
                        and flyBullets[1][i] + lengthBullets * sin > surfY \
                        and flyBullets[0][i] < surfX + WIDTH and flyBullets[1][i] < surfY + HEIGHT:
                    sin = math.sin(math.radians(flyBullets[2][i]))
                    cos = math.cos(math.radians(flyBullets[2][i]))
                    drawX = flyBullets[0][i] - surfX
                    drawY = flyBullets[1][i] - surfY
                    pygame.draw.line(screen, flyBullets[3][i], [drawX, drawY], [drawX - lengthBullets * cos, drawY - lengthBullets * sin], 1)
            SpringAllY -= 0.5
            for i in range(len(map["spring"][3])):
                if map["spring"][0][i] + map["spring"][2][i] > surfX and map["spring"][1][i] + \
                        map["spring"][3][i] > surfY \
                        and map["spring"][0][i] < surfX + WIDTH and map["spring"][1][i]-30 < surfY + HEIGHT:
                    pygame.draw.rect(screen, (235, 228, 30), (map["spring"][0][i] - surfX,
                                                              map["spring"][1][i] - surfY,
                                                              map["spring"][2][i], map["spring"][3][i]))
                    n = 3
                    for j in range(n):
                        ySPR = SpringAllY % 30 + 30 / n * j
                        if ySPR > 30:
                            ySPR -= 30
                        ySPR -= 30
                        pygame.draw.line(screen, (191, 149, 10),
                                         (map["spring"][0][i] - surfX, map["spring"][1][i] + ySPR - surfY),
                                         (map["spring"][0][i] + map["spring"][2][i] - surfX - 1,
                                          map["spring"][1][i] + ySPR - surfY), 2)
            if dash == "stop": 
                if xO < x and yO == y and grav == 0:
                    if anime != 0:
                        anime = 0
                        timeCadr = 0
                        cadr = 0
                    timeCadr += 1
                    if timeCadr >= FPS * GGRunSec // len(GGRun):
                        if cadr + 1 < len(GGRun):
                            cadr += 1
                        else:
                            cadr = 0
                        timeCadr = 0
                    if cadr + 1 >= len(GGRun):
                        cadr = 0
                    GG = GGRun[cadr]
                    GGRIGHT = True
                    DROP = False
                elif xO > x and yO == y and grav == 0:
                    if anime != 1:
                        anime = 1
                        timeCadr = 0
                        cadr = 0
                    timeCadr += 1
                    if timeCadr >= FPS * GGRunSec // len(GGRun):
                        if cadr + 1 < len(GGRun):
                            cadr += 1
                        else:
                            cadr = 0
                        timeCadr = 0
                    if cadr + 1 >= len(GGRun):
                        cadr = 0
                    GG = GGRun[cadr]
                    GGRIGHT = False
                    DROP = False
                elif yO > y and xO == x and FlagWall == False:
                    if anime != 2:
                        anime = 2
                        timeCadr = 0
                        cadr = 0
                    timeCadr += 1
                    if timeCadr >= FPS * GGJumpSec // len(GGJump):
                        if cadr + 1 < len(GGJump):
                            cadr += 1
                        timeCadr = 0
                    if cadr + 1 > len(GGJump):
                        cadr = 0
                    GG = GGJump[cadr]
                    DROP = False
                elif yO < y and xO == x and FlagWall == False:
                    if anime != 3:
                        anime = 3
                        timeCadr = 0
                        cadr = 0
                    timeCadr += 1
                    if timeCadr >= FPS * GGJumpSec // len(GGJump):
                        if cadr + 1 < len(GGJump):
                            cadr += 1
                        timeCadr = 0
                    if cadr + 1 > len(GGJump):
                        cadr = 0
                    GG = GGJump[cadr]
                    DROP = True
                elif yO > y and xO < x:
                    if anime != 2:
                        anime = 2
                        timeCadr = 0
                        cadr = 0
                    timeCadr += 1
                    if timeCadr >= FPS * GGJumpRunSec // len(GGJumpRun):
                        if cadr + 1 < len(GGJumpRun):
                            cadr += 1
                        timeCadr = 0
                    if cadr + 1 > len(GGJumpRun):
                        cadr = 0
                    GG = GGJumpRun[cadr]
                    DROP = False
                    GGRIGHT = True
                elif yO > y and xO > x:
                    if anime != 2:
                        anime = 2
                        timeCadr = 0
                        cadr = 0
                    timeCadr += 1
                    if timeCadr >= FPS * GGJumpRunSec // len(GGJumpRun):
                        if cadr + 1 < len(GGJumpRun):
                            cadr += 1
                        timeCadr = 0
                    if cadr + 1 > len(GGJumpRun):
                        cadr = 0
                    GG = GGJumpRun[cadr]
                    DROP = False
                    GGRIGHT = False
                elif yO < y and xO < x:
                    if anime != 3:
                        anime = 3
                        timeCadr = 0
                        cadr = 0
                    timeCadr += 1
                    if timeCadr >= FPS * GGJumpRunSec // len(GGJumpRun):
                        if cadr + 1 < len(GGJumpRun):
                            cadr += 1
                        timeCadr = 0
                    if cadr + 1 > len(GGJumpRun):
                        cadr = 0
                    GG = GGJumpRun[cadr]
                    DROP = True
                    GGRIGHT = True
                elif yO < y and xO > x:
                    if anime != 3:
                        anime = 3
                        timeCadr = 0
                        cadr = 0
                    timeCadr += 1
                    if timeCadr >= FPS * GGJumpRunSec // len(GGJumpRun):
                        if cadr + 1 < len(GGJumpRun):
                            cadr += 1
                        timeCadr = 0
                    if cadr + 1 > len(GGJumpRun):
                        cadr = 0
                    GG = GGJumpRun[cadr]
                    DROP = True
                    GGRIGHT = False
                elif yO == y and xO == x and grav == 0 or (FlagWall and int(math.sqrt((xO-x)**2 + (yO-y)**2) < 4)):
                    if anime != 4:
                        anime = 4
                        timeCadr = 0
                        cadr = 0
                    timeCadr += 1
                    if timeCadr >= FPS * GGStopSec // len(GGStop):
                        if cadr + 1 < len(GGStop):
                            cadr += 1
                        else:
                            cadr = 0
                        timeCadr = 0
                    if cadr + 1 >= len(GGStop):
                        cadr = 0
                    GG = GGStop[cadr]
                    if lastButton == "right":
                        GGRIGHT = True
                    else:
                        GGRIGHT = False
                    DROP = False
            elif dash == "motion":
                if anime != -1:
                    anime = -1
                    cadr = 0
                    timeCadr = 0
                timeCadr += 1
                if timeCadr >= FPS * GGDashSec // len(GGDash):
                    if cadr + 1 < len(GGDash):
                        cadr += 1
                    timeCadr = 0
                if NDash == "up" or NDash == "down" or NDash == "left" or NDash == "right":
                    GG = GGDash[cadr]
                    if NDash == "up":
                        DROP = False
                    elif NDash == "down":
                        DROP = True
                    if NDash == "right":
                        rotate = "right"
                    elif NDash == "left":
                        rotate = "left"
                else:
                    GG = GGDashRun[cadr]
                    if NDash[:2] == "up":
                        DROP = False
                    else:
                        DROP = True
                    if NDash[-5:] == "right":
                        GGRIGHT = True
                    else:
                        GGRIGHT = False
            for i in range(len(GG[0])):
                drawX = x + GG[0][i] - surfX
                drawY = y + GG[1][i] - surfY
                if rotate == "none":
                    if FlagWall and int(math.sqrt((xO-x)**2 + (yO-y)**2) < 4):
                        if canJumpWallL == True:
                            drawY = y - GG[0][i] - 3 - surfY + Size
                            drawX = x + GG[1][i] - surfX
                            GGRIGHT = True
                            DROP = False
                        elif canJumpWallR == True:
                            drawX = x - GG[1][i] - 3 - surfX + Size
                            drawY = y + GG[0][i] - surfY
                            GGRIGHT = True
                            DROP = True
                    if GGRIGHT == False:
                        drawX = x - (drawX - x + surfX) - surfX + Size - 3
                    if DROP:
                        drawY = y - (drawY - y + surfY) - surfY + Size - 3
                else:
                    if rotate == "left":
                        drawY = y - GG[0][i] - 3 - surfY + Size
                        drawX = x + GG[1][i] - surfX
                    else:
                        drawX = x - GG[1][i] - 3 - surfX + Size
                        drawY = y + GG[0][i] - surfY
                lol = GG[2][i]
                if canDash == False:
                    if GG[2][i] == (0, 190, 0):
                        lol = (0, 190, 190)
                    elif GG[2][i] == (0, 95, 0):
                        lol = (0, 95, 95)
                pygame.draw.rect(screen, lol, (drawX, drawY, 3, 3))
            rotate = "none"
            timeCadrSpikes += 1
            if timeCadrSpikes >= FPS * SpikesSec // len(SpikesTexture):
                if cadrSpikes + 1 < len(SpikesTexture):
                    cadrSpikes += 1
                else:
                    cadrSpikes = 0
                timeCadrSpikes = 0
            SpikesTex = SpikesTexture[cadrSpikes]
            for i in range(len(map["spikes"][3])):
                if map["spikes"][0][i] + map["spikes"][2][i] > surfX and map["spikes"][1][i] + map["spikes"][3][i] > surfY \
                        and map["spikes"][0][i] < surfX + WIDTH and map["spikes"][1][i] < surfY + HEIGHT:
                    pygame.draw.rect(screen, (225, 225, 225), (map["spikes"][0][i]-surfX, map["spikes"][1][i]-surfY, map["spikes"][2][i], map["spikes"][3][i]))
                    for w in range(map["spikes"][2][i]//10):
                        for j in range(len(SpikesTex[0])):
                            drawX = map["spikes"][0][i] + SpikesTex[0][j] - surfX + 10 * w
                            drawY = map["spikes"][1][i] + SpikesTex[1][j] - surfY
                            if drawX + surfX + 1 > surfX and drawY + surfY + 2 > surfY \
                                    and drawX + surfX < surfX + WIDTH and drawY + surfY < surfY + HEIGHT:
                                pygame.draw.rect(screen, SpikesTex[2][j], (drawX, drawY, 2, 2))
                    for h in range(map["spikes"][2][i] // 10):
                        for j in range(len(SpikesTex[0])):
                            drawX = map["spikes"][0][i] + SpikesTex[0][j] - surfX + 10 * h
                            drawY = map["spikes"][1][i] - SpikesTex[1][j] - surfY + map["spikes"][3][i]-2
                            if drawX + surfX + 1 > surfX and drawY + surfY + 2 > surfY \
                                    and drawX + surfX < surfX + WIDTH and drawY + surfY < surfY + HEIGHT:
                                pygame.draw.rect(screen, SpikesTex[2][j], (drawX, drawY, 2, 2))
            try:
                for i in range(len(map["enemyFly"][1])):
                    if map["enemyFly"][9][i] > 0:
                        if map["enemyFly"][0][i] + map["enemyFly"][2] > surfX \
                                and map["enemyFly"][1][i] + map["enemyFly"][3] > surfY \
                                and map["enemyFly"][0][i] < surfX + WIDTH and map["enemyFly"][1][i] < surfY + HEIGHT:
                            if map["enemyFly"][6][i] or map["enemyFly"][8][i] > 0:
                                if map["enemyFly"][-1][i] <= enemyFlySec * FPS:
                                    enemyFly = ENEMY1[
                                        min(map["enemyFly"][-1][i] // (enemyFlySec * FPS // len(ENEMY1)), len(ENEMY1) - 1)]
                                    map["enemyFly"][-1][i] += 1
                                else:
                                    map["enemyFly"][-1][i] = 0
                                    enemyFly = ENEMY1[0]
                            else:
                                enemyFly = ENEMYSTAN1
                            for j in range(len(enemyFly[0])):
                                drawX = map["enemyFly"][0][i] + enemyFly[0][j] - surfX
                                drawY = map["enemyFly"][1][i] + enemyFly[1][j] - surfY
                                pygame.draw.rect(screen, enemyFly[2][j], (drawX, drawY, 3, 3))
                            if map["enemyFly"][9][i] < hpEnemyFly:
                                pygame.draw.line(screen, (50, 50, 50), [map["enemyFly"][0][i] - surfX,
                                                                               map["enemyFly"][1][i] - 6 - surfY],
                                                 [map["enemyFly"][0][i] + map["enemyFly"][2] - surfX,
                                                  map["enemyFly"][1][i] - 6 - surfY], 3)
                                pygame.draw.line(screen, (180, 10, 10), [map["enemyFly"][0][i] - surfX,
                                                                               map["enemyFly"][1][i] - 6 - surfY],
                                                 [map["enemyFly"][0][i] + map["enemyFly"][2] * (map["enemyFly"][9][i]/hpEnemyFly) - surfX, map["enemyFly"][1][i] - 6 - surfY], 3)
            except:
                pass
            for i in range(len(map["block"][3])):
                if map["block"][0][i] + map["block"][2][i] > surfX and map["block"][1][i] + map["block"][3][i] > surfY \
                        and map["block"][0][i] < surfX + WIDTH and map["block"][1][i] < surfY + HEIGHT:
                    pygame.draw.rect(screen, (38, 38, 38), (map["block"][0][i]-surfX, map["block"][1][i]-surfY, map["block"][2][i],
                                                     map["block"][3][i]))
                    n1 = 4
                    n2 = 4
                    if map["block"][2][i] <= 30:
                        n1 = 1
                    elif map["block"][2][i] <= 50:
                        n1 = 2
                    elif map["block"][2][i] <= 100:
                        n1 = 3
                    if map["block"][3][i] <= 30:
                        n2 = 1
                    elif map["block"][3][i] <= 50:
                        n2 = 2
                    elif map["block"][3][i] <= 100:
                        n2 = 3
                    for j in range(n1+1):
                        pygame.draw.line(screen, (101, 201, 200), (map["block"][0][i] + map["block"][2][i]/n1*j-surfX, map["block"][1][i]-surfY), (map["block"][0][i] + map["block"][2][i]/n1*j-surfX, map["block"][1][i]+map["block"][3][i]-surfY), 1)
                    for j in range(n2+1):
                        pygame.draw.line(screen, (101, 201, 200), (map["block"][0][i]-surfX, map["block"][1][i] + map["block"][3][i]/n2*j-surfY), (map["block"][0][i]+map["block"][2][i]-surfX, map["block"][1][i] + map["block"][3][i]/n2*j-surfY), 1)
            pygame.draw.rect(screen, (38, 38, 38), (0, minY - surfY, WIDTH, -minY + surfY + HEIGHT))
            pygame.draw.line(screen, (101, 201, 200), (0, minY - surfY), (WIDTH, minY - surfY))
            fps = int(clock.get_fps())
            textFPS = font.render('FPS: ' + str(fps), 1, WHITE)
            textX = font.render('X: ' + str(int(x)), 1, WHITE)
            textY = font.render('Y: ' + str(int(y)), 1, WHITE)
            textSpeed = font.render('Speed: ' + str(int(math.sqrt((xO-x)**2 + (yO-y)**2))), 1, WHITE)
            textGame = font.render('GameMode: ' + str(gameMode), 1, WHITE)
            textType = font.render('Type: ' + str(createType), 1, WHITE)
            for gunnn in range(1):
                if mouseY < -surfY + y + Size // 2:
                    angle = -(math.acos((mouseX - (-surfX + x + Size // 2)) / ((mouseX - (-surfX + x + Size // 2)) ** 2 + (
                                mouseY - (-surfY + y + Size // 2)) ** 2) ** 0.5)) * 360 / math.pi / 2
                else:
                    angle = (math.acos((mouseX - (-surfX + x + Size//2)) / ((mouseX - (-surfX + x + Size//2)) ** 2 + (
                            mouseY - (-surfY + y + Size // 2)) ** 2) ** 0.5)) * 360 / math.pi / 2
                for gu in range(len(Gun[0])):
                    drawX = Gun[0][gu]
                    drawY = Gun[1][gu]
                    color = Gun[2][gu]
                    pygame.draw.rect(GunSurf, color, (drawX, drawY, 2, 2))
                if math.fabs(angle) > 90:
                    GunSurfR = pygame.transform.flip(GunSurf, False, True)
                    pivotGun = [int(-surfX + x + Size // 2), int(-surfY + y + Size // 2)]
                    offsetGun = pygame.math.Vector2(GunSurf.get_width()-24, 3)
                else:
                    GunSurfR = pygame.transform.flip(GunSurf, False, False)
                    pivotGun = [int(-surfX + x + Size // 2), int(-surfY + y + Size // 2)]
                    offsetGun = pygame.math.Vector2(7, -3)
                rotated_Gun, rect = rotate1(GunSurfR, angle, pivotGun, offsetGun)
                screen.blit(rotated_Gun, rect)
            if bulletTime > 0:
                bulletTime -= 1
                bulletsCadr = min(bullets * 2 + 1, 32)
            else:
                bulletsCadr = bullets * 2
            for bu in range(len(BULLETS[bulletsCadr][0])):
                drawX = BULLETS[bulletsCadr][0][bu]
                drawY = BULLETS[bulletsCadr][1][bu]
                pygame.draw.rect(screen, colorBullets, (inventory[0] + drawX, inventory[1] + drawY, 4, 4))
            for buM in range(len(BULLETSMAX[0][0])):
                drawX = BULLETSMAX[0][0][buM]
                drawY = BULLETSMAX[0][1][buM]
                pygame.draw.rect(screen, colorBullets, (inventory[0] + drawX + 62, inventory[1] + drawY, 4, 4))
            if canCreate:
                screen.blit(textX, (10, 30))
                screen.blit(textY, (10, 50))
                screen.blit(textSpeed, (10, 70))
                screen.blit(textGame, (10, 90))
                screen.blit(textFPS, (10, 10))
            if gameMode == "creat":
                screen.blit(textType, (10, 110))
                if draw == 1:
                    if createType != "rollback" and createType != "spawnpoint" and createType != "bullets" and createType != "enemyFly" and createType != "finish":
                        pygame.draw.rect(screen, pygame.Color('red'), (
                            map[createType][0][-1] - surfX, map[createType][1][-1] - surfY,
                            mouseX + surfX - map[createType][0][-1],
                            mouseY + surfY - map[createType][1][-1]), 1)
                    else:
                        try:
                            pygame.draw.rect(screen, pygame.Color('red'), (
                                mouseX - map[createType][2]//2, mouseY - map[createType][3]//2,
                                mouseX + map[createType][2]//2 - (mouseX - map[createType][2]//2),
                                mouseY + map[createType][3]//2 - (mouseY - map[createType][3]//2)), 1)
                        except:
                            map["bullets"] = [[], [], 15, 15, [], []]
                            map["enemyFly"] = [[], [], 21, 21, [], [], [], [[], [], [], []], [], [], []]
                            map["finish"] = [[], [], 24, 24]
                            pygame.draw.rect(screen, pygame.Color('red'), (
                                mouseX - map[createType][2] // 2, mouseY - map[createType][3] // 2,
                                mouseX + map[createType][2] // 2 - (mouseX - map[createType][2] // 2),
                                mouseY + map[createType][3] // 2 - (mouseY - map[createType][3] // 2)), 1)
                elif draw == 2:
                    pygame.draw.rect(screen, pygame.Color('blue'), (firstMouseX, firstMouseY, mouseX-firstMouseX, mouseY-firstMouseY), 1)
                elif draw == -1:
                    for i in range(len(correctObject["block"])):
                        pygame.draw.rect(screen, pygame.Color('blue'),
                                         (-surfX+map["block"][0][correctObject["block"][i]],
                                          -surfY+map["block"][1][correctObject["block"][i]],
                                          map["block"][2][correctObject["block"][i]],
                                          map["block"][3][correctObject["block"][i]]), 2)
                    for i in range(len(correctObject["spikes"])):
                        pygame.draw.rect(screen, pygame.Color('blue'),
                                         (-surfX + map["spikes"][0][correctObject["spikes"][i]],
                                          -surfY + map["spikes"][1][correctObject["spikes"][i]],
                                          map["spikes"][2][correctObject["spikes"][i]],
                                          map["spikes"][3][correctObject["spikes"][i]]), 2)
                    for i in range(len(correctObject["spring"])):
                        pygame.draw.rect(screen, pygame.Color('blue'),
                                         (-surfX+map["spring"][0][correctObject["spring"][i]],
                                          -surfY+map["spring"][1][correctObject["spring"][i]],
                                          map["spring"][2][correctObject["spring"][i]],
                                          map["spring"][3][correctObject["spring"][i]]), 2)
                    for i in range(len(correctObject["background"])):
                        pygame.draw.rect(screen, pygame.Color('blue'),
                                         (-surfX+map["background"][0][correctObject["background"][i]],
                                          -surfY+map["background"][1][correctObject["background"][i]],
                                          map["background"][2][correctObject["background"][i]],
                                          map["background"][3][correctObject["background"][i]]), 2)
                    for i in range(len(correctObject["rollback"])):
                        pygame.draw.rect(screen, pygame.Color('blue'),
                                         (-surfX+map["rollback"][0][correctObject["rollback"][i]],
                                          -surfY+map["rollback"][1][correctObject["rollback"][i]],
                                          map["rollback"][2],
                                          map["rollback"][3]), 2)
                    for i in range(len(correctObject["spawnpoint"])):
                        pygame.draw.rect(screen, pygame.Color('blue'),
                                         (-surfX+map["spawnpoint"][0][correctObject["spawnpoint"][i]],
                                          -surfY+map["spawnpoint"][1][correctObject["spawnpoint"][i]],
                                          map["spawnpoint"][2],
                                          map["spawnpoint"][3]), 2)
                    for i in range(len(correctObject["bullets"])):
                        pygame.draw.rect(screen, pygame.Color('blue'),
                                         (-surfX+map["bullets"][0][correctObject["bullets"][i]],
                                          -surfY+map["bullets"][1][correctObject["bullets"][i]],
                                          map["bullets"][2],
                                          map["bullets"][3]), 2)
                    for i in range(len(correctObject["enemyFly"])):
                        pygame.draw.rect(screen, pygame.Color('blue'),
                                         (-surfX+map["enemyFly"][0][correctObject["enemyFly"][i]],
                                          -surfY+map["enemyFly"][1][correctObject["enemyFly"][i]],
                                          map["enemyFly"][2],
                                          map["enemyFly"][3]), 2)
                    for i in range(len(correctObject["finish"])):
                        pygame.draw.rect(screen, pygame.Color('blue'),
                                         (-surfX+map["finish"][0][correctObject["finish"][i]],
                                          -surfY+map["finish"][1][correctObject["finish"][i]],
                                          map["finish"][2],
                                          map["finish"][3]), 2)
                if createType == "background":
                    for i in range(len(backColor)):
                        pygame.draw.rect(screen, backColor[i], (WIDTH-30-i*30, 0, 30, 30))
                        if createColor == backColor[i]:
                            pygame.draw.rect(screen, WHITE, (WIDTH - 30 - i * 30, 0, 30, 30), 2)
        if grav == 0 and yO == y and xO != x:
            if playSoundRun == 1:
                runSound.play(-1)
                playSoundRun = 0
        else:
            if playSoundRun == 0:
                runSound.stop()
                playSoundRun = 1
        if grav == 0 and yO < y:
            dropSound.play()
        xO = x
        yO = y
    virtual_display = pygame.transform.scale(screen, current_size)
    screen0.blit(virtual_display, (0, 0))
    pygame.display.update()
    clock.tick(FPS)
pygame.quit()