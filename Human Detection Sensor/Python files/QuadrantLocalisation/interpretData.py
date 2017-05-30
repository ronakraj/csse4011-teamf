import csv
import pandas as pd
import numpy as np
from sklearn import svm

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

clf = svm.SVC(decision_function_shape='ovo')

def remove_nans(matrix):
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if (np.isnan(matrix[i][j]) == True):
                if i > 0:
                    matrix[i][j] = matrix[i-1][j]
                    
def svm_train():
    global clf

    quad_1 = pd.read_csv('quad1 (copy).csv')
    quad_2 = pd.read_csv('quad2 (copy).csv')
    quad_3 = pd.read_csv('quad3 (copy).csv')
    quad_4 = pd.read_csv('quad4 (copy).csv')

    # data set
    quad_1 = quad_1.as_matrix()
    quad_2 = quad_2.as_matrix()
    quad_3 = quad_3.as_matrix()
    quad_4 = quad_4.as_matrix()

    # labels
    quad_1_labels = np.ones(quad_1.shape[0])
    quad_2_labels = np.ones(quad_2.shape[0]) * 2
    quad_3_labels = np.ones(quad_3.shape[0]) * 3
    quad_4_labels = np.ones(quad_4.shape[0]) * 4

    # remove nans
    remove_nans(quad_1)
    remove_nans(quad_2)
    remove_nans(quad_3)
    remove_nans(quad_4)
    
    data = np.concatenate((quad_1, quad_2, quad_3, quad_4), axis=0)
    #print data
    
    labels = np.concatenate((quad_1_labels, quad_2_labels, \
       quad_3_labels, quad_4_labels), axis=0)

    # Split to training and testing groups
    # data1, data2, target1, target2 = train_test_split(data, \
    #                                                   labels, \
    #                                                   test_size=0.8, \
    #                                                   random_state=42)
    
    #print data, labels
    clf = svm.SVC(decision_function_shape='ovo')
    
    clf.fit(data, labels)
 
def svm_classify(input_data):
    split_data = input_data.split(',')
    temp = [int(split_data[0]), int(split_data[1]), int(split_data[2]), int(split_data[3])]
    #print temp
    data = np.array(temp).reshape((1,-1))
    
    prediction = clf.predict(data)
    print prediction

# read loop for serial port
def read_loop():
  global i

  output = ''
  svm_train()
  
  while read_data:
    try:
      data = s.read();
      if len(data) > 0:
        output += data
        if (data[-1]=='\n'):
           #print output
           svm_classify(output)
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
