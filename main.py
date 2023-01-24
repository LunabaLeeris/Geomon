import math

from kivy import Config
from kivy.app import App
import os

Config.set('graphics', 'resizable', True)
Config.set('graphics', 'width', 800)
Config.set('graphics', 'height', 800)

from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.properties import Clock
from kivy.uix.relativelayout import RelativeLayout

Player_Sprites = {'Player_Front1': os.path.join('assets', 'player', 'Player_Front1.png'),
                  'Player_Front2': os.path.join('assets', 'player', 'Player_Front2.png'),
                  'Player_Front3': os.path.join('assets', 'player', 'Player_Front3.png'),
                  'Player_Left1': os.path.join('assets', 'player', 'Player_Left1.png'),
                  'Player_Left2': os.path.join('assets', 'player', 'Player_Left2.png'),
                  'Player_Left3': os.path.join('assets', 'player', 'Player_Left3.png'),
                  'Player_Right1': os.path.join('assets', 'player', 'Player_Right1.png'),
                  'Player_Right2': os.path.join('assets', 'player', 'Player_Right2.png'),
                  'Player_Right3': os.path.join('assets', 'player', 'Player_Right3.png'),
                  'Player_Back1': os.path.join('assets', 'player', 'Player_Back1.png'),
                  'Player_Back2': os.path.join('assets', 'player', 'Player_Back2.png'),
                  'Player_Back3': os.path.join('assets', 'player', 'Player_Back3.png')
                  }

Assets_Path = {'MapDark': os.path.join('assets', 'MiniMapDark.png'),
               'Poles': os.path.join('assets', 'Poles.png'),
               'Trees': os.path.join('assets', 'Trees.png'),
               'Rain1': os.path.join('assets', 'Rain1.png'),
               'Rain2': os.path.join('assets', 'Rain2.png'),
               'Rain3': os.path.join('assets', 'Rain3.png'),
               'Rain4': os.path.join('assets', 'Rain4.png'),
               'rdrop1': os.path.join('assets', 'rdrop1.png'),
               'rdrop2': os.path.join('assets', 'rdrop2.png'),
               'rdrop3': os.path.join('assets', 'rdrop3.png'),
               'Clouds': os.path.join('assets', 'Clouds.png')}


class MainWin(RelativeLayout):
    def __init__(self, **kwargs):
        # KeyBoards
        super().__init__(**kwargs)
        self.keyboard = Window.request_keyboard(self.on_keyboard_closed, self)
        self.keyboard.bind(on_key_down=self.on_keyboard_down)
        self.keyboard.bind(on_key_up=self.on_keyboard_up)
        self.keys_pressed = []
        # Collisions:
        self.pole_position = {110: 550, 263: 405, 127: 195, 364: 466, 387: 552, 544: 569, 506: 438, 416: 285, 582: 287,
                              296: 103, 616: 80, 583: 20, 255: 191}
        self.tree_position = {208: 535, 253: 499, 90: 542, 85: 503, 242: 584, 350: 352, 316: 302, 300: 330, 352: 184,
                              336: 100, 522: 220, 587: 120}
        self.house_positions = {402: (317, 113, 72), 508: (271, 120, 116), 377: (82, 128, 56)}
        self.wall_position = {0: (559, 302, 60), 40: (273, 34, 315), 74: (374, 5, 46), 1:(203, 91, 73), 110:(203, 60, 73)}

        # Dimensions
        self.p_vel = .004
        self.h_vel = 0
        self.y_vel = 0
        self.image_pos_x = self.width * 0
        self.image_pos_y = self.height * 0
        self.char_pos_x = 0
        self.char_pos_y = 0
        self.pole_added = False
        self.tree_added = False
        # Images
        self.background_image = Image(source=Assets_Path['MapDark'], pos=(self.image_pos_x, self.image_pos_y),
                                      allow_stretch=True, size_hint=(3, 3))
        self.bg_w = self.background_image.width
        self.poles = Image(source=Assets_Path['Poles'], allow_stretch=True, size_hint=(3, 3))
        self.trees = Image(source=Assets_Path['Trees'], allow_stretch=True, size_hint=(3, 3))
        self.char = Image(source=Player_Sprites['Player_Front1'], allow_stretch=True, size_hint=(3, 3),
                          pos=(self.center_x, self.center_y))
        self.char.center_x = self.width*.5
        self.char.center_y = self.height*.5
        self.clouds = Image(source=Assets_Path['Clouds'], pos=(self.image_pos_x, self.image_pos_y),
                            allow_stretch=True, size_hint=(3, 3))
        # Maths
        self.FPS = 60
        self.p_percent_width = .019
        self.p_percent_height = 0.04
        self.t_percent_width = .04
        self.t_percent_height = .065
        self.p_increment_width = self.p_percent_width * self.background_image.width
        self.p_increment_height = -self.p_percent_height * self.background_image.height
        self.t_increment_width = self.t_percent_width * self.background_image.width
        self.t_increment_height = self.t_percent_height * self.background_image.height
        # For Rain Effects
        self.rain1 = Image(source=Assets_Path['Rain1'], allow_stretch=True, size_hint=(3, 3))
        self.rain2 = Image(source=Assets_Path['Rain2'], allow_stretch=True, size_hint=(3, 3))
        self.rain3 = Image(source=Assets_Path['Rain3'], allow_stretch=True, size_hint=(3, 3))
        self.rain4 = Image(source=Assets_Path['Rain4'], allow_stretch=True, size_hint=(3, 3))
        self.rdrop = Image(source=Assets_Path['rdrop1'], allow_stretch=True, size_hint=(3, 3))
        # For Animation Increments
        self.rain_pos = 1
        self.rdrop_pos = 1
        self.char_pos = 1
        # Determines the direction of the character 0=front, 1=left, 2=back, 3=right
        self.direction = 0

        self.add_image_objects()

        # Game Grid
        self.rc = 700
        self.grid_pos = []
        self.prev_position = (0, 0)
        self.prev_obj_on_prev_pos = 0

        # Main Game lopp
        Clock.schedule_interval(self.adjust_game, 1 / self.FPS)
        # Rain Line Loop
        Clock.schedule_interval(self.rain, 1 / 12)
        # Rain Droplets Loop
        Clock.schedule_interval(self.rDrop, 1 / 9)
        # Character Animation Loop
        Clock.schedule_interval(self.Char, 1 / 9)
        self.draw_grid()

    def Char(self, dt):
        if self.direction == 0:
            if self.char_pos == 1:
                self.char.source = Player_Sprites['Player_Front1']
                self.char_pos = 2
            elif self.char_pos == 2:
                self.char.source = Player_Sprites['Player_Front2']
                self.char_pos = 3
            elif self.char_pos == 3:
                self.char.source = Player_Sprites['Player_Front3']
                self.char_pos = 1
        elif self.direction == 2:
            if self.char_pos == 1:
                self.char.source = Player_Sprites['Player_Back1']
                self.char_pos = 2
            elif self.char_pos == 2:
                self.char.source = Player_Sprites['Player_Back2']
                self.char_pos = 3
            elif self.char_pos == 3:
                self.char.source = Player_Sprites['Player_Back3']
                self.char_pos = 1
        elif self.direction == 1:
            if self.char_pos == 1:
                self.char.source = Player_Sprites['Player_Left1']
                self.char_pos = 2
            elif self.char_pos == 2:
                self.char.source = Player_Sprites['Player_Left2']
                self.char_pos = 3
            elif self.char_pos == 3:
                self.char.source = Player_Sprites['Player_Left3']
                self.char_pos = 1
        elif self.direction == 3:
            if self.char_pos == 1:
                self.char.source = Player_Sprites['Player_Right1']
                self.char_pos = 2
            elif self.char_pos == 2:
                self.char.source = Player_Sprites['Player_Right2']
                self.char_pos = 3
            elif self.char_pos == 3:
                self.char.source = Player_Sprites['Player_Right3']
                self.char_pos = 1

    def rDrop(self, dt):
        if self.rdrop_pos == 1:
            self.rdrop.source = Assets_Path['rdrop1']
            self.rdrop_pos = 2
        elif self.rdrop_pos == 2:
            self.rdrop.source = Assets_Path['rdrop2']
            self.rdrop_pos = 3
        elif self.rdrop_pos == 3:
            self.rdrop.source = Assets_Path['rdrop3']
            self.rdrop_pos = 1

    def rain(self, dt):
        if self.rain_pos == 1:
            self.rain2.pos = self.background_image.pos
            self.remove_widget(self.rain1)
            self.add_widget(self.rain2)
            self.rain_pos = 2
        elif self.rain_pos == 2:
            self.rain3.pos = self.background_image.pos
            self.remove_widget(self.rain2)
            self.add_widget(self.rain3)
            self.rain_pos = 3
        elif self.rain_pos == 3:
            self.rain1.pos = self.background_image.pos
            self.remove_widget(self.rain3)
            self.add_widget(self.rain4)
            self.rain_pos = 4
        elif self.rain_pos == 4:
            self.rain1.pos = self.background_image.pos
            self.remove_widget(self.rain4)
            self.add_widget(self.rain1)
            self.rain_pos = 1

    def adjust_game(self, dt):
        self.adjust_vel()
        self.adjust_background(dt)
        self.adjust_image_obj()

    def on_size(self, *args):
        self.char.size_hint = (.35, .35)

    def add_image_objects(self):
        self.add_widget(self.clouds)
        self.add_widget(self.rain1)
        self.add_background_image()
        self.add_widget(self.rdrop)

        self.add_char()

    def adjust_image_obj(self):
        self.poles.pos = self.background_image.pos
        self.trees.pos = self.background_image.pos
        self.rdrop.pos = self.background_image.pos

    # -----------------------------CONVERSION TO GRID STUFF-------------------------------------

    def draw_grid(self):
        self.initialize_grid()
        self.draw_poles()
        self.draw_trees()
        self.draw_houses()
        self.draw_walls()

    def initialize_grid(self):
        for i in range(self.rc):
            self.grid_pos.append([])
            for j in range(self.rc):
                self.grid_pos[i].append(0)

    def draw_trees(self):
        for i in self.tree_position:
            x = int(round((i / 700) * self.rc, 0))
            y = int(round((self.tree_position[i] / 700) * self.rc, 0))
            h = int(round(self.t_percent_height * self.rc, 0))
            w = int(round(self.t_percent_width * self.rc, 0))
            s = self.get_bottom_collision()
            for j in range(y - h, y + 1):
                for k in range(x - w, x + w + 1):
                    self.grid_pos[j][k] = 'T'

            for k in range(y + 1, y + 1 + s):
                for l in range(x - int(s), x + int(s) + 1):
                    self.grid_pos[k][l] = 'X'

    def draw_houses(self):
        for i in self.house_positions:
            x = int(round((i / 700) * self.rc, 0))
            y = int(round((self.house_positions[i][0] / 700) * self.rc, 0))
            w = int(round((self.house_positions[i][1] / 700) * self.rc, 0))
            h = int(round((self.house_positions[i][2] / 700) * self.rc, 0))

            for j in range(y, y + h):
                for k in range(x, x + w):
                    self.grid_pos[j][k] = 'X'

    def draw_poles(self):
        for i in self.pole_position:
            x = int(round((i / 700) * self.rc, 0))
            y = int(round((self.pole_position[i] / 700) * self.rc, 0))
            h = int(round(self.p_percent_height * self.rc, 0))
            w = int(round(self.p_percent_width * self.rc, 0))
            s = self.get_bottom_collision()

            for j in range(y - h, y + 1):
                for k in range(x - w, x + w + 1):
                    self.grid_pos[j][k] = 'P'

            for k in range(y + 1, y + 1 + s):
                for l in range(x - int(s), x + int(s) + 1):
                    self.grid_pos[k][l] = 'X'

    def draw_walls(self):
        for i in self.wall_position:
            x = int(round((i / 700) * self.rc, 0))
            y = int(round((self.wall_position[i][0] / 700) * self.rc, 0))
            w = int(round((self.wall_position[i][1] / 700) * self.rc, 0))
            h = int(round((self.wall_position[i][2] / 700) * self.rc, 0))

            for j in range(y, y + h):
                for k in range(x, x + w):
                    self.grid_pos[j][k] = 'X'

    def get_bottom_collision(self):
        size = math.ceil(.011 * self.rc)
        return size

    def print_grid(self):
        for i in range(self.rc):
            print(' ')
            for j in range(self.rc):
                print(self.grid_pos[i][j], end=' ')

    def adjust_player_grid_pos(self):
        x, y = self.get_pos_on_grid()
        if x == self.rc:
            x = self.rc - 1
        if y == self.rc:
            y = self.rc - 1
        self.grid_pos[self.prev_position[1]][self.prev_position[0]] = self.prev_obj_on_prev_pos
        self.prev_position = (x, y)
        self.prev_obj_on_prev_pos = self.grid_pos[y][x]
        self.grid_pos[y][x] = '1'
        print(x, y)

    def check_for_collision(self):
        if self.prev_obj_on_prev_pos == 'P' and not self.pole_added:
            self.add_widget(self.poles)
            self.pole_added = True
        elif self.prev_obj_on_prev_pos == 'T' and not self.tree_added:
            self.add_widget(self.trees)
            self.tree_added = True
        elif self.prev_obj_on_prev_pos == 0:
            if self.pole_added:
                self.remove_widget(self.poles)
                self.pole_added = False
            if self.tree_added:
                self.remove_widget(self.trees)
                self.tree_added = False

    def get_pos_on_grid(self):
        x = int(((-self.image_pos_x + self.char_pos_x) / self.background_image.width) * self.rc)
        y = int(((self.background_image.height + self.image_pos_y - self.char_pos_y) / self.background_image.height) * self.rc)
        return x, y

    # -------------------------------------PLAYER STUFF-------------------------------------

    def add_char(self):
        self.add_widget(self.char)

    # -------------------------------------BACKGROUND STUFF----------------------------------

    def check_border(self, x, y, time_factor):
        move_background = True
        self.char_pos_x, self.char_pos_y = self.char.center_x, self.char.center_y

        if x > 0 and self.h_vel > 0:
            self.char_pos_x -= self.h_vel * time_factor
            move_background = False
            return move_background
        if y > 0 and self.y_vel > 0:
            self.char_pos_y -= self.y_vel * time_factor
            move_background = False
            return move_background
        if abs(x) >= self.background_image.width - self.width and self.h_vel < 0:
            self.char_pos_x -= self.h_vel * time_factor
            move_background = False
            return move_background
        if abs(y) >= self.background_image.height - self.height and self.y_vel < 0:
            self.char_pos_y -= self.y_vel * time_factor
            move_background = False
            return move_background

        if self.y_vel != 0 and self.char_pos_y != self.center_y:
            self.char_pos_y -= self.y_vel * time_factor
            move_background = False
            if self.y_vel < 0 and self.char_pos_y > self.center_y:
                print(y)
                self.char_pos_y = self.center_y
                return move_background
            if self.y_vel > 0 and self.char_pos_y < self.center_y:
                self.char_pos_y = self.center_y
                return move_background

        elif self.h_vel != 0 and self.char_pos_x != self.center_x:
            self.char_pos_x -= self.h_vel * time_factor
            move_background = False
            if self.h_vel < 0 and self.char_pos_x > self.center_x:
                self.char_pos_x = self.center_x
                return move_background
            if self.h_vel > 0 and self.char_pos_x < self.center_x:
                self.char_pos_x = self.center_x
                return move_background

        return move_background

    def adjust_background(self, dt):
        time_factor = self.FPS * dt
        result = self.check_border(self.image_pos_x + self.h_vel * time_factor, self.image_pos_y + self.y_vel * time_factor, time_factor)
        if result:
            self.image_pos_x += self.h_vel * time_factor
            self.image_pos_y += self.y_vel * time_factor
            self.update_background_image_pos()
            self.adjust_player_grid_pos()
            self.check_for_collision()
            return
        else:
            self.update_char_image_pos()

    def update_char_image_pos(self):
        x, y = self.get_pos_on_grid()
        if self.grid_pos[y][x] == 'X':
            self.char_pos_x = self.char.center_x
            self.char_pos_y = self.char.center_y

        else:
            self.char.center_x = self.char_pos_x
            self.char.center_y = self.char_pos_y

    def update_background_image_pos(self):
        x, y = self.get_pos_on_grid()
        if self.grid_pos[y][x] == 'X':
            self.image_pos_x, self.image_pos_y = self.background_image.pos
        else:
            # updates background position
            self.background_image.pos = (self.image_pos_x, self.image_pos_y)

    def adjust_vel(self):
        self.h_vel = 0
        self.y_vel = 0
        if len(self.keys_pressed) > 0:
            if self.keys_pressed[0] == 'w':
                self.y_vel = -self.p_vel * self.height
                self.direction = 2
            elif self.keys_pressed[0] == 'a':
                self.h_vel = self.p_vel * self.width
                self.direction = 1
            elif self.keys_pressed[0] == 's':
                self.y_vel = self.p_vel * self.height
                self.direction = 0
            elif self.keys_pressed[0] == 'd':
                self.h_vel = -self.p_vel * self.width
                self.direction = 3

    def add_background_image(self):
        self.add_widget(self.background_image)

    # -------------------------------------KEYBOARD STUFF----------------------------------
    def on_keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard.unbind(on_key_up=self.on_keyboard_up)
        self.keyboard = None

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if len(self.keys_pressed) < 2 and keycode[1] not in self.keys_pressed:
            self.keys_pressed.append(keycode[1])

    def on_keyboard_up(self, keyboard, keycode):
        if keycode[1] in self.keys_pressed:
            self.keys_pressed.remove(keycode[1])


class Geomon(App):
    pass


if __name__ == '__main__':
    Geomon().run()
