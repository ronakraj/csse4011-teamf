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


i = 0

# read loop for serial port
def read_loop():
  global i

  output = ''
  while read_data:
    try:
      data = s.read();
      if len(data) > 0:
        output += data
        if (data[-1]=='\n'):

           fd = file('quad1.csv', 'a')
           fd.write(output)
           fd.close()
           print "*** CAPTURED ***    ", i, '\n'
           print output
           i = i + 1

           output = ''
           data = s.read()
    except Exception, e:
      pass


  # close serial port
  print "close serial port"
  s.close()


# init serial port
s = serial.Serial(port = '/dev/ttyACM0', baudrate = 115200) #TIVA


# start read_loop in a separate thread
read_data = True
t1 = threading.Thread(target=read_loop, args=())
t1.start()