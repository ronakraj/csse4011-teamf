import socket
import time
import select

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
from copy import deepcopy

from bs4 import BeautifulSoup
import urllib

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import numpy as np
import pylab
import math
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report,confusion_matrix
import csv
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score
import urllib
import requests

# mlp = MLPClassifier(activation='relu', alpha=0.0001, batch_size='auto', beta_1=0.9,
#            beta_2=0.999, early_stopping=False, epsilon=1e-08,
#            hidden_layer_sizes=(20), learning_rate='constant',
#            learning_rate_init=0.15, max_iter=1000, momentum=0.45,
#            nesterovs_momentum=True, power_t=0.5, random_state=None,
#            shuffle=True, solver='adam', tol=0.0001, validation_fraction=0.1,
#            verbose=False, warm_start=False)

mlp = MLPClassifier(activation='relu', alpha=0.0001, batch_size='auto', beta_1=0.9,
           beta_2=0.999, early_stopping=False, epsilon=1e-08,
           hidden_layer_sizes=(20), learning_rate='constant',
           learning_rate_init=0.1, max_iter=10000, momentum=0.5,
           nesterovs_momentum=True, power_t=0.5, random_state=None,
           shuffle=True, solver='adam', tol=0.0001, validation_fraction=0.1,
           verbose=False, warm_start=False) 

calibrating = 1
serial_data = ''

url = "http://192.168.4.1/SWAP2"

UDP_IP = "192.168.43.112"
UDP_PORT = 12345
 # UDP

def calibrate_specific(prompt, filename, num_samples, sock):

  print prompt
  time.sleep(1)
  print "5.."
  time.sleep(1)
  print "4.."
  time.sleep(1)
  print "3.."
  time.sleep(1)
  print "2.."
  time.sleep(1)
  print "1.."
  time.sleep(1)
  print "Calibrating..."

  count = 0
  fd = open(filename, "w")
  fd.write(" ")
  fd.close()
  fd = open(filename, "a")

  while count < num_samples:

    count += 1

    sock.sendto("q{0}".format(0), (UDP_IP, UDP_PORT))
    ready = select.select([sock], [], [], 2)

    if ready[0]:
      data, addr = sock.recvfrom(1024)
      #split_data = data.split(',')
      #temp = [int(split_data[0]), int(split_data[1]), int(split_data[2]), int(split_data[3]), \
      #int(split_data[4]), int(split_data[5]), int(split_data[6]), int(split_data[7])]
      #new_data = [np.mean([temp[0], temp[2]]), np.mean([temp[1], temp[3]]), np.mean([temp[4], temp[6]]), np.mean([temp[5], temp[7]])]
      #print data
      #data_string = str(int(new_data[0])) + ',' + str(int(new_data[1])) + ','  + str(int(new_data[2])) + ','  + str(int(new_data[3])) + '\n'
      print data
      fd.write(data)

    time.sleep(0.05)

  print "Finished."

  fd.close()

def calibrate(filenames, sock):

  num_samples = 250

  calibrate_specific("Remove everything from sensor area.", filenames[0], num_samples, sock)
  calibrate_specific("Place hand in 1st quadrant.", filenames[1], num_samples, sock)
  calibrate_specific("Place hand in 2nd quadrant.", filenames[2], num_samples, sock)
  calibrate_specific("Place hand in 3rd quadrant.", filenames[3], num_samples, sock)
  calibrate_specific("Place hand in 4th quadrant.", filenames[4], num_samples, sock)

  print "Calibration complete."

def svm_classify(input_data):
    split_data = input_data.split(',')
    temp = [int(split_data[0]), int(split_data[1]), int(split_data[2]), int(split_data[3]), \
        int(split_data[4]), int(split_data[5]), int(split_data[6]), int(split_data[7])]
    #data = [np.mean([temp[0], temp[2]]), np.mean([temp[1], temp[3]]), np.mean([temp[4], temp[6]]), np.mean([temp[5], temp[7]])]
    #print temp
    #print data
    new_data = np.array(temp).reshape((1,-1))

    prediction = mlp.predict(new_data)
    return prediction
    #print prediction

def remove_nans(matrix):
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if (np.isnan(matrix[i][j]) == True):
                if i > 0:
                    matrix[i][j] = matrix[i-1][j]

def train_learner_mlp(filenames):#, e, f):
    global mlp

    swipe_a = pd.read_csv(filenames[1])
    swipe_a = swipe_a.as_matrix()
    remove_nans(swipe_a)
    swipe_a_class = np.ones(swipe_a.shape[0]) * 1

    swipe_b = pd.read_csv(filenames[2])
    swipe_b = swipe_b.as_matrix()
    remove_nans(swipe_b)
    swipe_b_class = np.ones(swipe_b.shape[0]) * 2

    swipe_c = pd.read_csv(filenames[3])
    swipe_c = swipe_c.as_matrix()
    remove_nans(swipe_c)
    swipe_c_class = np.ones(swipe_c.shape[0]) * 3

    swipe_d = pd.read_csv(filenames[4])
    swipe_d = swipe_d.as_matrix()
    remove_nans(swipe_d)
    swipe_d_class = np.ones(swipe_d.shape[0]) * 4

    swipe_e = pd.read_csv(filenames[0])
    swipe_e = swipe_e.as_matrix()
    remove_nans(swipe_e)
    swipe_e_class = np.ones(swipe_e.shape[0]) * 0

    X = np.concatenate((swipe_a, swipe_b, swipe_c, swipe_d, swipe_e), axis=0)#, swipe_e, swipe_f), axis=0)
    y = np.concatenate((swipe_a_class, swipe_b_class, swipe_c_class, \
        swipe_d_class, swipe_e_class), axis=0)#, swipe_e_class, swipe_f_class), axis=0)

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
    time.sleep(1);
    print confusion_matrix(y_test,predictions)
    print classification_report(y_test,predictions)
    print mlp.score(X_test, y_test)
    print scores
    time.sleep(1);


def run():

  #filenames = ["backupcal/empty (copy).csv", "backupcal/quad1 (copy).csv", "backupcal/quad2 (copy).csv", "backupcal/quad3 (copy).csv", "backupcal/quad4 (copy).csv"]
  filenames = ["empty.csv", "quad1.csv", "quad2.csv", "quad3.csv", "quad4.csv"]

  #calibrate(filenames)

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.setblocking(0)

  #calibrate(filenames, sock)

  train_learner_mlp(filenames)

  #fd = open("quad4.csv")

  # for line in fd:
  #   print svm_classify(line)

  
  data = ''
  result = [0]

  while True:

    try:
      result = svm_classify(data) 
      print result
    except Exception:
      print "ERROR"

    time.sleep(0.1)

    sock.sendto("q{0}".format(int(result[0])), (UDP_IP, UDP_PORT))

    time.sleep(0.1)

    ready = select.select([sock], [], [], 2)

    if ready[0]:
      data, addr = sock.recvfrom(1024)
      print data



if __name__ == "__main__":
  run()