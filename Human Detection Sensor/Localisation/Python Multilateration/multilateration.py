"""
This demo demonstrates how to draw a dynamic matplotlib
plot in a wxPython application.

This code is based on Eli Bendersky's code found here:
http://eli.thegreenplace.net/files/prog_code/wx_mpl_dynamic_graph.py.txt

"""

import os
import random
import wx
import serial
import threading
import json
import time
import readchar

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import numpy as np
import pylab
import math

distanceIR1 = 0
distanceIR2 = 0
distanceIR3 = 0
distanceIR4 = 0

ir1_pos[2] = [0, 0]
ir2_pos[2] = [0, 0]
ir3_pos[2] = [0, 0]
ir4_pos[2] = [0, 0]

#Parse JSON
def parse_json(json_output):

    global distanceIR1
    global distanceIR2
    global distanceIR3
    global distanceIR4

    if json_output.startswith('{'):
        try:
            j = json.loads(json_output)
            ir1 = j['IR1']
            ir2 = j['IR2']
            ir3 = j['IR3']
            ir4 = j['IR4']
            distanceIR1 = log(j['IR1'] + 1.91 / 1390.014) / -0.403;

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

            xPos, yPos = np.linalg.lstsq(a, b)[0]
            print "X: ", xPos, "cm Y: ", yPos, " cm\n\r"

        except Exception, e:
            pass


# read loop for serial port
def read_loop():

  output = ''
  while read_data:
    try:
      data = s.read();
      if len(data) > 0:
        output += data
        if (data[-1]=='\n'):
           parse_json(output)
           output = ''
           data = s.read()
    except Exception, e:
      pass


  # close serial port
  print "close serial port"
  s.close()


# init serial port
s = serial.Serial(port = 'COM8', baudrate = 115200) #TIVA


# start read_loop in a separate thread
read_data = True
t1 = threading.Thread(target=read_loop, args=())
t1.start()
