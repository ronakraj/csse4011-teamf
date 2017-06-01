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

def svm_classify(input_data):
    split_data = input_data.split(',')
    temp = [int(split_data[0]), int(split_data[1]), int(split_data[2]), int(split_data[3])]
    #print temp
    data = np.array(temp).reshape((1,-1))
    
    prediction = mlp.predict(data)
    print prediction

def remove_nans(matrix):
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if (np.isnan(matrix[i][j]) == True):
                if i > 0:
                    matrix[i][j] = matrix[i-1][j]
                    
def train_learner_mlp(a, b, c, d):#, e, f):
    global mlp
    
    swipe_a = pd.read_csv(a)
    swipe_a = swipe_a.as_matrix()
    remove_nans(swipe_a)
    swipe_a_class = np.ones(swipe_a.shape[0]) * 1

    swipe_b = pd.read_csv(b)
    swipe_b = swipe_b.as_matrix()
    remove_nans(swipe_b)
    swipe_b_class = np.ones(swipe_b.shape[0]) * 2

    swipe_c = pd.read_csv(c)
    swipe_c = swipe_c.as_matrix()
    remove_nans(swipe_c)
    swipe_c_class = np.ones(swipe_c.shape[0]) * 3

    swipe_d = pd.read_csv(d)
    swipe_d = swipe_d.as_matrix()
    remove_nans(swipe_d)
    swipe_d_class = np.ones(swipe_d.shape[0]) * 4

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
    print confusion_matrix(y_test,predictions)
    print classification_report(y_test,predictions)
    print mlp.score(X_test, y_test)
    print scores

# read loop for serial port
def read_loop():

  # Setup MLP with test data
  #train_learner_mlp('13_swipe.csv', '24_swipe.csv', '31_swipe.csv', '42_swipe.csv', \
  #  'clockwise.csv', 'anticlockwise.csv')
  
  train_learner_mlp('quad1 (copy).csv', 'quad2 (copy).csv', 'quad3 (copy).csv', 'quad4 (copy).csv')#, \
  #  'clockwise.csv', 'anticlockwise.csv')
  
  output = ''
  while read_data:
    try:
      data = s.read();
      if len(data) > 0:
        output += data
        if (data[-1]=='\n'):
           #parse_json(output)
           svm_classify(output)
           output = ''
           #data = s.read()
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
