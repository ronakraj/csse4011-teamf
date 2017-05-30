#!/usr/bin/python
import pygame
from pygame.locals import *
from gameobjects.vector2 import Vector2
from copy import *
import numpy as np
import serial
import os
import random
import wx
import serial
import threading
import json
import time
import readchar

import numpy as np
import pylab
import math
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report,confusion_matrix
import csv
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score

mlp = MLPClassifier(activation='relu', alpha=0.0001, batch_size='auto', beta_1=0.9,
           beta_2=0.999, early_stopping=False, epsilon=1e-08,
           hidden_layer_sizes=(20), learning_rate='constant',
           learning_rate_init=0.4, max_iter=10000, momentum=0.5,
           nesterovs_momentum=True, power_t=0.5, random_state=None,
           shuffle=True, solver='adam', tol=0.0001, validation_fraction=0.1,
           verbose=False, warm_start=False) 

SCREEN_X, SCREEN_Y = 400, 400
HALF_X, HALF_Y = SCREEN_X/2, SCREEN_Y/2
SENSOR_RANGE = (-2500, 2500, -2500, -1250)

sensor_position = Vector2(0, 0)
distanceIR1 = 0
distanceIR2 = 0
distanceIR3 = 0
distanceIR4 = 0

ir1_pos = [-0.9, 0]
ir2_pos = [0, 0.9]
ir3_pos = [0.9, 0]
ir4_pos = [0, -0.9]

prediction = 0

def parse_json(json_output):

    global distanceIR1
    global distanceIR2
    global distanceIR3
    global distanceIR4
    global ir1_pos
    global ir2_pos
    global ir3_pos
    global ir4_pos
    global prediction

    if json_output.startswith('{'):
        try:
            j = json.loads(json_output)

           #print j
            
            ir1 = j['IR1'] 
            ir2 = j['IR2'] 
            ir3 = j['IR3'] 
            ir4 = j['IR4'] 

            ir13_s = j['IR13S']
            ir24_s = j['IR24S']
            ir13_f = j['IR13F']
            ir24_f = j['IR24F']
            ir1_iter = j['IR1T'] # iterations of sensor 1 peaks
            ir2_iter = j['IR2T'] # iterations of sensor 2 peaks
            ir3_iter = j['IR3T'] # iterations of sensor 3 peaks
            ir4_iter = j['IR4T'] # iterations of sensor 4 peaks

            if (ir13_s != 0 or ir24_s != 0):
                temp = [ir13_s, ir24_s, ir13_f, ir24_f, ir1_iter, ir2_iter, ir3_iter]
                data = np.array(temp).reshape((1,-1))
                prediction = mlp.predict(data)
                prediction = prediction[0]
                print prediction
                print ir13_s, ir24_s, ir13_f, ir24_f
            else:
                prediction = 0

            # ln1 = (ir1 + 191) / 1390.014
            # ln2 = (ir2 + 191) / 1390.014
            # ln3 = (ir3 + 191) / 1390.014
            # ln4 = (ir4 + 191) / 1390.014

            ln1 = (ir1 - 1364.1) / (-14.555)
            ln2 = (ir2 - 1364.1) / (-14.555)
            ln3 = (ir3 - 1364.1) / (-14.555)
            ln4 = (ir4 - 1364.1) / (-14.555)

            distanceIR1 = ln1
            distanceIR2 = ln2
            distanceIR3 = ln3
            distanceIR4 = ln4

            ln1 = max(ln1, 0)
            ln2 = max(ln2, 0)
            ln3 = max(ln3, 0)
            ln4 = max(ln4, 0)
            #if ln1 > 0 and ln2 > 0 and ln3 > 0 and ln4 > 0:
                #distanceIR1 = log(j['IR1'] + 191 / 1390.014) / -0.403;
                # maybe seperate multilaterations
                # distanceIR1 = np.log((ir1 + 191) / 1390.014) / -0.403 * 10;
                # distanceIR2 = np.log((ir2 + 191) / 1390.014) / -0.403 * 10;
                # distanceIR3 = np.log((ir3 + 191) / 1390.014) / -0.403 * 10;
                # distanceIR4 = np.log((ir4 + 191) / 1390.014) / -0.403 * 10;
                #print distanceIR1, distanceIR2, distanceIR3, distanceIR4

            #distanceIR1 = np.log(ln1) / (-0.0005) / 100
            #distanceIR2 = np.log(ln2) / (-0.0005) / 100
            #distanceIR3 = np.log(ln3) / (-0.0005) / 100
            #distanceIR4 = np.log(ln4) / (-0.0005) / 100

            b = np.array([[distanceIR1**2 - distanceIR4**2 \
                    - ir1_pos[0]**2 - ir1_pos[1]**2 + ir4_pos[0]**2 + \
                    ir4_pos[1]**2], [distanceIR2**2 - \
                    distanceIR4**2 - ir2_pos[0]**2 - ir2_pos[1]**2 + \
                    ir4_pos[0]**2 + ir4_pos[1]**2], \
                    [distanceIR3**2 - distanceIR4**2 \
                    - ir3_pos[0]**2 - ir3_pos[1]**2 + ir4_pos[0]**2 + \
                    ir4_pos[1]**2]])
            a = np.array([[2*(ir4_pos[0] - ir1_pos[0]), \
                    2*(ir4_pos[1] - ir1_pos[1])], \
                    [2*(ir4_pos[0] - ir2_pos[0]), \
                    2*(ir4_pos[1] - ir2_pos[1])], \
                    [2*(ir4_pos[0] - ir3_pos[0]), \
                    2*(ir4_pos[1] - ir3_pos[1])]])
                
            #print distanceIR1, distanceIR2, distanceIR3, distanceIR4
            xPos, yPos = np.linalg.lstsq(a, b)[0]
            #print "ORIGINAL: X: ", xPos[0], "mm Y: ", yPos[0], " mm\n\r"

            sensor_position.x = xPos[0]
            sensor_position.y = yPos[0]

        except Exception, e: 
            print e

def train_learner_mlp(a, b, c, d, e, f):
    global mlp

    swipe_a = pd.read_csv(a)
    swipe_a = swipe_a.as_matrix()
    swipe_a_class = np.ones(swipe_a.shape[0])*13

    swipe_b = pd.read_csv(b)
    swipe_b = swipe_b.as_matrix()
    swipe_b_class = np.ones(swipe_b.shape[0]) * 24

    swipe_c = pd.read_csv(c)
    swipe_c = swipe_c.as_matrix()
    swipe_c_class = np.ones(swipe_c.shape[0]) * 31

    swipe_d = pd.read_csv(d)
    swipe_d = swipe_d.as_matrix()
    swipe_d_class = np.ones(swipe_d.shape[0]) * 42

    # swipe_e = pd.read_csv(e)
    # swipe_e = swipe_e.as_matrix()
    # #swipe_d = swipe_d[:,0:8]
    # swipe_e_class = np.ones(swipe_e.shape[0]) * 0

    # swipe_f = pd.read_csv(f)
    # swipe_f = swipe_f.as_matrix()
    # #swipe_d = swipe_d[:,0:8]
    # swipe_f_class = np.ones(swipe_f.shape[0]) * 1

    X = np.concatenate((swipe_a, swipe_b,  swipe_c, swipe_d), axis=0)#, swipe_e, swipe_f), axis=0)
    y = np.concatenate((swipe_a_class, swipe_b_class, swipe_c_class, \
        swipe_d_class), axis=0)#, swipe_e_class, swipe_f_class), axis=0)

    X_train, X_test, y_train, y_test = train_test_split(X, y)

    scaler = StandardScaler(copy=True, with_mean=True, with_std=True)
    # Fit only to the training data
    scaler.fit(X_train)

    # Now apply the transformations to the data:
    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)

    mlp.fit(X_train,y_train)

    predictions = mlp.predict(X_test)
    scores = cross_val_score(mlp, X_test, y_test, cv=10)

def read_loop():
    # Setup MLP with test data
    train_learner_mlp('13_swipe.csv', '24_swipe.csv', '31_swipe.csv', '42_swipe.csv', \
        'clockwise.csv', 'anticlockwise.csv')
    output = ''
    while read_data:
        try:
            data = s.read();
            if len(data) > 0:
                output += data
            if (data[-1]=='\n'):
                parse_json(output)
                output = ''
        except Exception, e:
            print "Exception:", e

    # close serial port
    print "close serial port"
    s.close()

read_data = True
s = serial.Serial(port = '/dev/ttyACM0', baudrate = 115200) #SensorTag
t1 = threading.Thread(target=read_loop, args=())
t1.start()

def map_val(x, in_min, in_max, out_min, out_max):

    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def blit_alpha(target, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pygame.Surface((source.get_width(), source.get_height())).convert()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)        
        target.blit(temp, location)

class Window(object):

    def __init__(self, size, flags):

        self.screen = pygame.display.set_mode(size, flags)
        self.clock = pygame.time.Clock()
        self.entities = []
        self.size = size
        self.flags = flags

    def add_entity(self, entity):

        self.entities.append(entity)

    def update_window(self, size):

        self.screen = pygame.display.set_mode(size, self.flags)

    def update(self):

        time_passed = self.clock.tick(60)
        time_passed_seconds = time_passed / 1000.0

        for e in self.entities:
            e.update(time_passed_seconds)

    def render(self):

        self.screen.fill((50, 50, 50))

        for e in self.entities:
            e.render(self.screen)

class Grid2D(object):

    def __init__(self, size, margins, res):

        self.user_pos = Vector2(0, 0)
        self.margins = margins
        self.res = res
        self.size = size
        self.t_points = []
        self.b_points = []
        self.l_points = []
        self.r_points = []
        self.update_points(size)
        self.prev_points = []

    def update_points(self, size):

        self.t_points = []
        self.b_points = []
        self.l_points = []
        self.r_points = []

        self.t_margin = self.margins[0]
        self.b_margin = size[1] - self.margins[1]
        self.l_margin = self.margins[2]
        self.r_margin = size[0] - self.margins[3]

        h_step = (self.r_margin - self.l_margin) / float(self.res)
        v_step = (self.b_margin - self.t_margin) / float(self.res)

        # Top / Bottom
        for x in range(self.res + 1):
            self.t_points.append(Vector2(x * h_step + self.l_margin, self.t_margin))
            self.b_points.append(Vector2(x * h_step + self.l_margin, self.b_margin))

        # Left / Right
        for y in range(self.res + 1):
            self.l_points.append(Vector2(self.l_margin, y * v_step + self.t_margin))
            self.r_points.append(Vector2(self.r_margin, y * v_step + self.t_margin))

    def update_pos(self, pos):

        x = map_val(pos.x, SENSOR_RANGE[0], SENSOR_RANGE[1], self.l_margin, self.r_margin)
        y = map_val(pos.y, SENSOR_RANGE[1], SENSOR_RANGE[2], self.t_margin, self.b_margin)

        self.user_pos.x = x
        self.user_pos.y = y

        if len(self.prev_points) > 100:
            self.prev_points = self.prev_points[1:]
        self.prev_points.append((x, y))

    def update(self, time_passed_seconds):
        pass

    def render(self, screen):
        
        for i in range(self.res + 1):
            pygame.draw.line(screen, (0, 0, 0), self.t_points[i], self.b_points[i])

        for j in range(self.res + 1):
            pygame.draw.line(screen, (0, 0, 0), self.l_points[j], self.r_points[j])

        if len(self.prev_points) >= 2:

            for k in range(len(self.prev_points) - 1):
                pygame.draw.line(screen, (255, 0, 0), self.prev_points[k], self.prev_points[k+1], 2)

        pygame.draw.circle(screen, (255, 0, 0), (int(self.user_pos.x), int(self.user_pos.y)), 7)

class GestureSprite(object):

    def __init__(self, image_path, pos, colour):

        self.alpha = 0
        self.image = pygame.image.load(image_path)
        self.image.convert_alpha()
        self.pos = pos
        self.colour = colour
        self.end_alpha = 0
        self.start_alpha = 0
        self.fade_time = 0

        self.start_pos = Vector2(0, 0)
        self.end_pos = Vector2(100, 100)
        self.vel = Vector2(0, 0)
        self.move_time = 0
        self.acc = 1.05
        self.fading = 0
        self.rotation = 0
        self.rot_vel = 0

    def fade(self, fade_time, start_alpha, end_alpha):

        self.start_alpha = start_alpha
        self.end_alpha = end_alpha
        self.fade_time = fade_time
        self.alpha = deepcopy(self.start_alpha)

    def move(self, move_time, start_pos, end_pos, rotation):

        self.rotation = rotation
        self.fade(0.2, 0, 255)
        self.fading = 0
        self.acc = 1.1
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.move_time = move_time 
        self.pos = deepcopy(start_pos)
        self.vel = (self.end_pos - self.start_pos).normalize() * Vector2.get_distance_to(self.start_pos, self.end_pos) / self.move_time

    def update(self, time_passed_seconds):

        if abs(int(self.alpha) - int(self.end_alpha)) > 4:
            self.alpha += (self.end_alpha - self.start_alpha) * (time_passed_seconds / self.fade_time)
            self.alpha = max(self.alpha, 0)

    def render(self, screen):

        blit_alpha(screen, pygame.transform.rotate(self.image, self.rotation), self.pos, self.alpha)

class SwipeSprite(GestureSprite):

    def __init__(self, image_path, pos, colour):

        GestureSprite.__init__(self, image_path, pos, colour)

    def update(self, time_passed_seconds):

        GestureSprite.update(self, time_passed_seconds)

        distance_to_end = Vector2.get_distance_to(self.pos, self.end_pos)
        distance_to_cover = Vector2.get_distance_to(self.start_pos, self.end_pos)

        if distance_to_end > 5:

            if distance_to_end < 60 and self.fading == 0:
                self.fade(0.2, 255, 0)
                self.fading = 1

            if abs(distance_to_end - distance_to_cover/2) < 5:
                self.acc = 0.9

            self.vel *= self.acc
            self.pos += self.vel * time_passed_seconds

class SwirlSprite(GestureSprite):

    def __init__(self, image_path, pos, colour):

        GestureSprite.__init__(self, image_path, pos, colour)

    def rotate(self, direction):

        self.fade(0.2, 0, 255)
        self.rotation = 1
        self.fading = 0
        self.acc = 1.0
        self.rot_vel = 5 * direction

    def update(self, time_passed_seconds):
        
        GestureSprite.update(self, time_passed_seconds)

        if self.rotation != 0:

            self.rot_vel *= self.acc
            self.rotation += self.rot_vel

        if abs(self.rotation - 360) < 150:
            self.acc = 1

        if self.rotation > 50:
            self.fade(0.2, 255, 0)
            #self.acc = 0.9

        if abs(self.rotation - 360) < 10:
            self.rotation = 0

    def render(self, screen):

        orig_rect = self.image.get_rect()
        rot_image = pygame.transform.rotate(self.image, self.rotation)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()

        blit_alpha(screen, rot_image, self.pos, self.alpha)

def run():

    pygame.init()

    window = Window((SCREEN_X, SCREEN_Y), RESIZABLE)

    gs = SwipeSprite("arrow.png", Vector2(100, 100), (0, 200, 0))
    grid = Grid2D(window.size, (50, 50, 50, 50), 10)

    window.add_entity(grid)
    window.add_entity(gs)

    global prediction

    while True:

        mouse_pos = pygame.mouse.get_pos()

        # try:
        # 	command=readchar.readchar()
        # 	s.write(command)
        # 	time.sleep(1)
        # except KeyboardInterrupt:
        # 	print "Shutdown"
        # 	#break

        for event in pygame.event.get():

            if event.type == QUIT:
                return

            elif event.type == VIDEORESIZE:
                window.update_window(event.size)
                grid.update_points(event.size)
            elif event.type is pygame.MOUSEBUTTONDOWN:
                if event.button is 1:
                    pass

        if int(prediction) == 31:
            gs.move(1, Vector2(HALF_X - 100, HALF_Y), Vector2(HALF_X, HALF_Y), 0)
        elif int(prediction) == 13:
            gs.move(1, Vector2(HALF_X, HALF_Y), Vector2(HALF_X - 100, HALF_Y), 180)
        elif int(prediction) == 24:
            gs.move(1, Vector2(HALF_X, HALF_Y), Vector2(HALF_X, HALF_Y - 100), 90)
        elif int(prediction) == 42:
            gs.move(1, Vector2(HALF_X, HALF_Y - 100), Vector2(HALF_X, HALF_Y), 270) 
        else:
            pass    

        prediction = 0

        grid.update_pos(sensor_position)

        window.update()
        window.render()

        pygame.display.update()

    read_data = False
     
if __name__ == "__main__":
    run()
