import sys
import numpy as np
import theano
import theano.tensor as T
import load_data
import random as rd
import train_regression
import hyppar
import datapar
import argument_parser
import statistics
import file_io
import os
import time
print('******* Import complete *******')

t0=time.time()


# Remove existing output files
if os.path.isfile("ITER"):
    os.remove("ITER")
if os.path.isfile("OUT"):
    os.remove("OUT")

rd.seed()

argument_parser.parseArgs(sys.argv,sys.path[0])

# Read input file
file_io.wout("Reading input data...\n")
hyppar.setInput()

# Set up neural network structure
file_io.wout("\n Setting up CNN structure...")
hyppar.setStructureParameters()
t1=time.time()

# Handle dataset
file_io.wout("Loading dataset...")
datapar.loadDataPoints()

# Define training, validation and test sets
file_io.wout("Splitting dataset...")
datapar.splitDataset()
t2=time.time()

# Train
#if(hyppar.task=='classification'):
#    train_classification.TrainCNN()
#else:
file_io.wout("\nTraining the model...")
train_regression.TrainCNN()
t3=time.time()
# Save accumulated data 
statistics.saveAll()
t4=time.time()

file_io.wout("\n Time taken in total: "+str(t4-t0))
file_io.wout("\n Time taken in reading data and constructing model : "+str(t1-t0))
file_io.wout("\n Time taken in dataset handling                    : "+str(t2-t1))
file_io.wout("\n Time taken in training                            : "+str(t3-t2))
file_io.wout("\n Time taken in writing the parameters              : "+str(t4-t3))
