# First, fool the test script that we are in src folder
import sys
split_path = sys.path[0].split('/')
newpath=""
for i in range(len(split_path)-2):
    newpath=newpath+'/'+split_path[i]
newpath=newpath+'/src'
sys.path[0] = newpath
import theano
import theano.tensor as T
import numpy as np
import six.moves.cPickle as pickle
import gzip
import os
import random as rd
import load_data
import cnn

def test_RMSLE():
    A=np.ones((2,1))
    B=np.ones((2,1))
    A[0,0]=2
    A[1,0]=2

    y,y_pred,yy=load_data.shared_dataset(A,B,sample_size=2)
    cost=cnn.RMSLE(y,y_pred)
    assert (cost.eval() - np.sqrt(( np.log(2) - np.log(3) )**2 ) < 0.001 )
    

def test_MSE():
    A=np.zeros((2,1))
    B=np.zeros((2,1))
    A[0,0]=1
    A[1,0]=1

    y,y_pred,yy=load_data.shared_dataset(A,B,sample_size=2)
    cost=cnn.MSE(y,y_pred)
    assert (cost.eval() < 1.0001)
    assert (cost.eval() > 0.9999)
    

def negative_log_lik(y, p_y_given_x):
    # Called by test_convLayer
    rows = T.arange(y.shape[0])
    cols = y;
    log_prob = T.log(p_y_given_x)
    cost_log = -T.mean(log_prob[rows, cols])
    return cost_log

def errors(y, y_pred):
    # Called by test_convLayer 
    count_error = T.mean(T.neq(y_pred, y))
    return count_error


def test_fullyConnectedLayer():
    '''
    Test that the fully connected layer works. This trains sine function 
    for a FCNN with one hidden layer of 4 units. For visualization check test.py.
    NOTE: Activations are done out of FC layer, since for atomic calculations
          linear activation is used.
    '''
    pi=np.float32(3.14159265358)

    xtrain=np.linspace(0,7,300,dtype='float32')
    ytrain=np.sin(xtrain)

    Xtrain=np.zeros((300,1),dtype='float32')
    for i in range(300):
        Xtrain[i]=xtrain[i]

    Ytrain=np.sin(Xtrain)


    rng = np.random.RandomState(23455)

    x=T.matrix('x')
    y=T.matrix('y')

    [hout, params_1] = cnn.fullyConnectedLayer(
        rng=rng,
        data_input=x,
        num_in=1,
        num_out=4,
        activation=T.nnet.sigmoid)

    [y_pred_lin, params_2] = cnn.fullyConnectedLayer(
        rng=rng,
        data_input=T.tanh(hout),
        num_in=4,
        num_out=1,
        activation=cnn.linear_activation)
    y_pred=T.tanh(y_pred_lin)

    cost=cnn.MSE(y,y_pred)

    params = params_1 + params_2

    updates = cnn.gradient_updates_Adam(cost,params,0.05)

    train = theano.function(
        inputs=[x,y],
        outputs=[cost],
        updates=updates)
    
    for i in range(2000):
        cost_i=train(Xtrain,Ytrain)
    assert cost_i[0] < 0.015

def test_gradient_updates_Adam():
    # Find minimum of a parabola
    x = T.scalar('x')
    w = theano.shared(np.float32(100.0),borrow=True)
    h = T.mul(w,x)
    cost=T.sqr(h)
    
    updates=cnn.gradient_updates_Adam(cost,[w],np.float32(10.0))
    
    f=theano.function([x],cost,updates=updates)
    for i in range(100):
        cost_i=f(np.float32(1))
    assert cost_i < 0.06
    
    x2 = T.matrix('x2')
    w2 = theano.shared(np.float32(10.0),borrow=True)
    h2 = T.dot(x2,w2)
    cost2 = T.mean(T.sin(h2)**2+0.1*h2**2)

    updates2=cnn.gradient_updates_Adam(cost2,[w2],np.float32(0.1))

    f2=theano.function([x2],cost2,updates=updates2)
    for i in range(200):
        cost_i2=f2(np.ones((1,1),dtype='float32'))
    assert cost_i2 < 1
