import pgzrun
import random
import math
from pgzero.actor import Actor

WIDTH = 820
HEIGHT = 620
INITIAL_HEALTH = 3

GAME_OVER = "Game Over"
YOU_WIN = "You Win!"
RESTART_MESSAGE = "Press any key to Restart"

jump_sound = sounds.jump
menu_open = True
game_over = False
you_win = False
health = INITIAL_HEALTH
music_playing = True

platforms = {
    'platform1': Actor('platform1', (60, 290)),
    'platform2': Actor('platform2', (250, 360)),
    'platform3': Actor('platform3', (410, 300)),
    'platform5': Actor('platform5', (570, 275)),
    'platform4': Actor('platform4', (765, 250))
}

valid_platforms = ['platform1', 'platform2', 'platform3', 'platform5', 'platform4']



class Hero(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__('rabbit', *args, **kwargs)
        self.speed = 3
        self.gravity = 0.5
        self.dy = 0
        self.dx = 0 
        self.jumping = False
        self.falling = False
        self.jump_speed = 7
        self.long_jump_multiplier = 1.5
        self.jump_start_platform = None
        self.walking = False
        self.horizontal_velocity = 0
        self.animations = {
            'idle': ['rabbit', 'rabbit5', 'rabbit6'],
            'walk': ['rabbit','rabbit2'],
            'jump': ['rabbit1']
        }
        self.frame = 0
        self.frame_timer = 0
        self.frame_rate = 0.1
        self.current_position = (self.x, self.y)
        self.on_platform = False

    def align_with_platform(self, platform):
        self.y = platform.y - platform.height / 2 - self.height / 2
        self.current_position = (self.x, self.y)

    def update(self):
        self.update_movement()
        self.frame_timer += 1 / 60

        if not self.on_platform:
            self.dy += self.gravity
            self.y += self.dy 

        if self.jumping:
            self.dy += self.gravity
            self.x += self.horizontal_velocity
            self.y += self.dy
            self.falling = True
        else:
            self.falling = False

        self.check_platform_collision()

        if self.walking:
            if self.frame_timer >= self.frame_rate:
                self.frame_timer = 0
                self.frame = (self.frame + 1) % len(self.animations['walk'])
                self.image = self.animations['walk'][self.frame]
        else:
            if self.frame_timer >= self.frame_rate:
                self.frame_timer = 0
                self.frame = (self.frame + 1) % len(self.animations['idle'])
                self.image = self.animations['idle'][self.frame]

        self.check_boundaries()

        if self.on_platform:
            current_platform_name = self.get_current_platform()
            if current_platform_name:
                self.align_with_platform(platforms[current_platform_name])
            else:
                self.on_platform = False  

    def check_boundaries(self):
        if self.x < 0:
            self.x = 0
        elif self.x > WIDTH:
            self.x = WIDTH

    def check_platform_collision(self):
        self.on_platform = False
        for platform_name, platform in platforms.items():
            if platform_name not in valid_platforms:
                continue
            platform_x = platform.x
            platform_y = platform.y
            if (self.y + self.height / 2 >= platform_y - platform.height / 2 and
                self.y + self.height / 2 <= platform_y + platform.height / 2 and
                self.x + self.width / 2 > platform_x - platform.width / 2 and
                self.x - self.width / 2 < platform_x + platform.width / 2):
                self.y = platform_y - platform.height / 2 - self.height / 2
                self.dy = 0
                self.jumping = False
                self.on_platform = True
                self.horizontal_velocity = 0
                break

        if not self.on_platform:
            self.y += self.dy  


    def get_current_platform(self):
        for platform_name, platform in platforms.items():
            if platform_name not in valid_platforms:
                continue
            
            platform_x = platform.x
            platform_y = platform.y
            if (self.y + self.height / 2 >= platform_y - platform.height / 2 and
                self.y + self.height / 2 <= platform_y + platform.height / 2 and
                self.x + self.width / 2 > platform_x - platform.width / 2 and
                self.x - self.width / 2 < platform_x + platform.width / 2):
                return platform_name
        return None

    def walk_left(self):
        if self.on_platform:  
            self.walking = True
            self.dx = -self.speed

    def walk_right(self):
        if self.on_platform:  
            self.walking = True
            self.dx = self.speed


    def jump(self):
            if not self.jumping and self.on_platform:
                self.jumping = True
                self.dy = -self.jump_speed
                if keyboard.left:
                    self.horizontal_velocity = -self.speed * self.long_jump_multiplier
                elif keyboard.right:
                    self.horizontal_velocity = self.speed * self.long_jump_multiplier
                else:
                    self.horizontal_velocity = 0 
                
                self.on_platform = False
                self.jump_start_platform = self.get_current_platform()
                self.current_position = (self.x, self.y)

    def stop(self):
        self.walking = False
        self.dx = 0

    def update_movement(self):
        if self.dx != 0:
            self.x += self.dx

class Enemy(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__('bee', *args, **kwargs)
        self.animations = {
            'idle': ['bee'],
            'move': ['bee1', 'bee4']
        }
        self.frame = 0
        self.frame_timer = 0
        self.frame_rate = 0.1
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.speed = 0.5

    def update(self):
        self.frame_timer += 1 / 60
        if self.frame_timer >= self.frame_rate:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % len(self.animations['move'])
            self.image = self.animations['move'][self.frame]
        self.x += self.direction_x * self.speed
        self.y += self.direction_y * self.speed
        if self.x < 0 or self.x > WIDTH:
            self.direction_x *= -1
        if self.y < 0 or self.y > HEIGHT:
            self.direction_y *= -1

        self.check_platform_collision()

    def check_platform_collision(self):
        self.on_platform = False
        for platform_name, platform in platforms.items():
            if platform_name not in valid_platforms:
                continue
            platform_x = platform.x
            platform_y = platform.y
            if (self.y + self.height / 2 <= platform_y + platform.height / 2 and
                self.y + self.height / 2 >= platform_y - platform.height / 2 and
                self.x + self.width / 2 >= platform_x and
                self.x - self.width / 2 <= platform_x + platform.width):
                self.y = platform_y - self.height / 2
                self.on_platform = True
                break

def generate_enemy_position():
    while True:
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        platform1 = platforms['platform1']
        if not (platform1.x <= x <= platform1.x + platform1.width and
                platform1.y <= y <= platform1.y + platform1.height):
            return x, y

hero = Hero((platforms['platform1'].x + platforms['platform1'].width / 2, platforms['platform1'].y - 50))
enemies = [Enemy(generate_enemy_position()) for _ in range(5)]

def draw():
    screen.clear()
    screen.fill((252, 223, 205)) 
    
    for platform in platforms.values():
        screen.blit(platform.image, platform.topleft)
    
    screen.blit('header', (0, 0))
    screen.blit('footer', (0, 453))
    screen.blit('tree_big', (200, 110))
    screen.blit('flowers', (620, 140))

    if menu_open:
        draw_menu()
    elif game_over:
        screen.draw.text(GAME_OVER, center=(WIDTH / 2, HEIGHT / 2), fontsize=60, color="red")
        screen.draw.text(RESTART_MESSAGE, center=(WIDTH / 2, HEIGHT / 2 + 60), fontsize=30, color="white")
    elif you_win:
        screen.draw.text(YOU_WIN, center=(WIDTH / 2, HEIGHT / 2), fontsize=60, color="green")
        screen.draw.text(RESTART_MESSAGE, center=(WIDTH / 2, HEIGHT / 2 + 60), fontsize=30, color="white")
    else:
        hero.draw()
        for enemy in enemies:
            enemy.draw()

def update():
    if not menu_open and not game_over and not you_win:
        hero.update()
        for enemy in enemies:
            enemy.update()

        for enemy in enemies:
            if hero.colliderect(enemy):
                end_game()

        if hero.y + hero.height / 2 > HEIGHT - 10:
            end_game()
        
        if hero.colliderect(platforms['platform4']):
            win_game()

        current_platform_name = hero.get_current_platform()
        if current_platform_name:
            hero.align_with_platform(platforms[current_platform_name])
            hero.on_platform = True

jumping_key_pressed = False


def on_key_down(key):
    global jumping_key_pressed, menu_open

    if menu_open:
        if key == keys.S:
            menu_open = False
            restart_game()
        elif key == keys.M:
            toggle_music()
        elif key == keys.Q:
            exit()
    elif game_over or you_win:
        if key:
            restart_game()
    else:
        if key == keys.ESCAPE:
            menu_open = True
        elif key == keys.LEFT:
            hero.walk_left()
        elif key == keys.RIGHT:
            hero.walk_right()
        elif key == keys.UP and not jumping_key_pressed:
            jumping_key_pressed = True
            hero.jump()
            if jump_sound_playing:
                jump_sound.play()

def on_key_up(key):
    global jumping_key_pressed, menu_open

    if not menu_open:
        if key == keys.LEFT or key == keys.RIGHT:
            hero.stop()  
        elif key == keys.UP:
            jumping_key_pressed = False  

def draw_menu():
    
    menu_center_x = WIDTH / 2
    menu_center_y = HEIGHT / 2 - 100
    step = 40  
    screen.draw.text("Main Menu", center=(menu_center_x, menu_center_y - 50),fontsize=60,color="black")
    screen.draw.text("Start Game (S)",center=(menu_center_x, menu_center_y),fontsize=30,color="black")
    screen.draw.text("Toggle Music (M) - Double Tap to Toggle",center=(menu_center_x, menu_center_y + step),fontsize=30,color="black")
    screen.draw.text("Exit (Q)",center=(menu_center_x, menu_center_y + 2 * step),fontsize=30,color="black")
    screen.draw.text("Press 'Escape' to open menu",center=(menu_center_x, menu_center_y + 3 * step),fontsize=30,color="black")

music_playing = True
jump_sound_playing = True

def toggle_music():
    global music_playing, jump_sound_playing, jump_sound
    
    if music_playing:
        music.stop()
        music_playing = False
        jump_sound_playing = False
    else:
        music.play('background_melody')
        music_playing = True
        jump_sound_playing = True

    if not jump_sound_playing:
        jump_sound.stop()
    else:
        pass

def init_game():
    if music_playing:
        music.play('background_melody')


def exit():
    import sys
    sys.exit()

def restart_game():
    global menu_open, game_over, you_win, health, enemies
    menu_open = False
    game_over = False
    you_win = False
    health = INITIAL_HEALTH
    start_platform = platforms['platform1']
    hero.x = start_platform.x
    hero.y = start_platform.y - start_platform.height / 2 - hero.height / 2
    hero.align_with_platform(start_platform)  
    hero.dx = 0
    hero.dy = 0
    hero.jumping = False
    hero.falling = False
    hero.jump_speed = 7
    hero.horizontal_velocity = 0
    hero.on_platform = True
    enemies = [Enemy(generate_enemy_position()) for _ in range(5)]

def end_game():
    global game_over
    game_over = True
    hero.jumping = False
    hero.jump_speed = 0

def win_game():
    global you_win
    you_win = True

pgzrun.go()
