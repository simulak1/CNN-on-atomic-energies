import theano
import theano.tensor as T
import numpy as np
from theano.sandbox.rng_mrg import MRG_RandomStreams as RandomStreams
import matplotlib.pyplot as plt
import random as rd
import cnn
import hyppar
import datapar
import load_data
import statistics

def CNNStructure(input,mini_batch_size,rng):
    
    # Use: hyppar module
    Nchannel     = hyppar.Nchannel
    NCL          = hyppar.NCL
    NFC          = hyppar.NFC
    pool         = hyppar.pool
    filter       = hyppar.filter
    activation   = hyppar.activation
    image_spec_x = hyppar.image_spec_x
    image_spec_y = hyppar.image_spec_y
    fc_out        = hyppar.fc_out

    activation_function = []
    for i in range(NCL):
        if (activation[i]=="tanh"):
            activation_function.append(T.tanh)
        elif (activation[i]=="relu"):
            activation_function.append(T.nnet.relu)
        elif (activation[i]=="elu"):
            activation_function.append(T.nnet.elu)
        elif (activation[i]=="sigmoid"):
            activation_function.append(T.nnet.sigmoid)
        else :
            print(str(i+1)+": UNKNOWN ACTIVATION!!!!!!!!")

    fc_activation=[]
    for i in range(NFC):
        if (hyppar.fc_activation[i]=="tanh"):
            fc_activation.append(T.tanh)
        elif (hyppar.fc_activation[i]=="relu"):
            fc_activation.append(T.nnet.relu)
        elif (hyppar.fc_activation[i]=="elu"):
            fc_activation.append(T.nnet.elu)
        elif (hyppar.fc_activation[i]=="sigmoid"):
            fc_activation.append(T.nnet.sigmoid)
        elif (hyppar.fc_activation[i]=="softmax"):
            fc_activation.append(T.nnet.softmax)
        else:
            fc_activation=cnn.linear_activation

    cn_output = []
    params    = []
    # This is the loop of the convolutions
    for i in range(NCL):
        [layer_output, layer_params] = cnn.convLayer(
            rng,
            data_input=input,
            image_spec=(mini_batch_size, Nchannel[i], image_spec_x[i], image_spec_y[i]),
            filter_spec=(Nchannel[i+1], Nchannel[i], filter[i][0], filter[i][1]),
            pool_size=(pool[i][0],pool[i][1]),
            activation=activation_function[i])

        cn_output = cn_output + [layer_output]
        params = params + layer_params
        input = layer_output


    if(NCL>0):
        fc_layer_input = layer_output.flatten(2)
        num_in = Nchannel[NCL]*image_spec_x[-1]*image_spec_y[-1]
    else:
        fc_layer_input = input.flatten(2)
        num_in = image_spec_x[0]*image_spec_y[0]

    fc_output = []
    for i in range(NFC):
        # The fully connected layer operates on a matrix of
        [y_pred, fc_layer_params] = cnn.fullyConnectedLayer(
            rng=rng,
            data_input=fc_layer_input,
            num_in=num_in, # Is this unstylish? Maybe.
            num_out=fc_out[i],
            activation=fc_activation[i])

        num_in=fc_out[i]
        fc_output = fc_output + y_pred
        params = params + fc_layer_params
        fc_layer_input = y_pred
        
    return y_pred, cn_output, params
    

def TrainCNN():
    
    # Training, validation and test data
    valid_set_x, valid_set_y, valid_set = load_data.shared_dataset(
        datapar.Xval, datapar.Yval,
        sample_size=hyppar.Nval)
    train_set_x, train_set_y, train_set = load_data.shared_dataset(
        datapar.Xtrain, datapar.Ytrain,
        sample_size=hyppar.Ntrain)
    test_set_x, test_set_y, test_set = load_data.shared_dataset(
        datapar.Xtest, datapar.Ytest,
        sample_size=hyppar.Ntest)

    
    # Hyperparameters
    learning_rate   = hyppar.learning_rate
    num_epochs      = hyppar.Nepoch
    num_filters     = hyppar.Nchannel
    mini_batch_size = hyppar.mbs
    reg             = hyppar.reg

    # Random set for following activations
    rset = rd.sample(range(valid_set_x.get_value(borrow=True).shape[0]),mini_batch_size)
    
    # Seeding the random number generator
    rng = np.random.RandomState(23455)
    
    # Computing number of mini-batches
    n_train_batches = train_set_x.get_value(borrow=True).shape[0]
    n_valid_batches = valid_set_x.get_value(borrow=True).shape[0]
    n_test_batches = test_set_x.get_value(borrow=True).shape[0]
    n_train_batches //= mini_batch_size
    n_valid_batches //= mini_batch_size
    n_test_batches //= mini_batch_size
        
    print('train: %d batches, validation: %d batches, testing: %d batches'
          % (n_train_batches, n_valid_batches, n_test_batches))

    # mini-batch index
    mb_index = T.lscalar()
    # Coulomb matrices ( mini_batch_size x 80 x 80 matrix)
    x = T.matrix('x')
    # Target energies (1 x mini_batch_size)
    y = T.matrix('y')
    
    print('***** Constructing model ***** ')
    
    # Reshaping tensor of mini_batch_size set of images into a
    # 4-D tensor of dimensions: (mini_batch_size , 1 , in_x , in_y)
    xdim=hyppar.in_x
    ydim=hyppar.in_y
    layer0_input = x.reshape((mini_batch_size,1,xdim,ydim))

    # Define the CNN function
    y_pred,cn_output,params=CNNStructure(layer0_input,mini_batch_size,rng)

    # Cost that is minimised during stochastic descent. Includes regularization
    cost = hyppar.cost_function(y_pred,y)
    
    L2_reg=0
    for i in range(len(params)):
        L2_reg=L2_reg+T.mean(T.sqr(params[i][0]))

    cost=cost+reg*L2_reg
    
    # Creates a Theano function that computes the mistakes on the validation set.
    # This performs validation.
    
    # Note: the givens parameter allows us to separate the description of the
    # Theano model from the exact definition of the inputs variable. The 'key'
    # that is passed to the graph is subsituted with the data from the givens
    # parameter. In this demo we built the model with a regular Theano tensor
    # and we use givens to speed up the GPU. We swap the input index with a
    # slice corresponding to the mini-batch of the dataset to use.
    
    # mb_index is the mini_batch_index
    valid_model = theano.function(
        [mb_index],
        cost,
        givens={
            x: valid_set_x[
                mb_index * mini_batch_size:
                (mb_index + 1) * mini_batch_size
            ],
            y: valid_set_y[
                mb_index * mini_batch_size:
                (mb_index + 1) * mini_batch_size
            ]})

    test_model = theano.function(
        [mb_index],
        cost,
        givens={
            x: test_set_x[
                mb_index * mini_batch_size:
                (mb_index + 1) * mini_batch_size
            ],
            y: test_set_y[
                mb_index * mini_batch_size:
                (mb_index + 1) * mini_batch_size
            ]})
    
    predict = theano.function(
        [mb_index],
        y_pred,
        givens={
            x : valid_set_x[
                mb_index * mini_batch_size:
                (mb_index+1) * mini_batch_size
                
            ]})

    if (hyppar.NCL>0):
        get_activations = theano.function(
            [],
            cn_output,
            givens={x: valid_set_x[rset]})
    

    # Creates a function that updates the model parameters by SGD.
    # The updates list is created by looping over all
    # (params[i], grads[i]) pairs.
    updates = cnn.gradient_updates_Adam(cost,params,learning_rate)
    
    # Create a Theano function to train our convolutional neural network.
    train_model = theano.function(
        [mb_index],
        cost,
        updates=updates,
        givens={
            x: train_set_x[
                mb_index * mini_batch_size:
                (mb_index + 1) * mini_batch_size
            ],
            y: train_set_y[
                mb_index * mini_batch_size:
                (mb_index + 1) * mini_batch_size
            ]})

        
    iter = 0
    epoch = 0
    cost_ij = 0
    valid_losses = [valid_model(i) for i in range(n_valid_batches)]
    valid_score = np.mean(valid_losses)

    train_error = []
    valid_error= []

    statistics.saveParameters(params)

     # This is where we call the previously defined Theano functions.
    print('***** Training model *****')
    while (epoch < num_epochs):
        epoch = epoch + 1
        for minibatch_index in range(n_train_batches):
            # Compute number of iterations performed or total number
            # of mini-batches executed.
            iter = (epoch - 1) * n_train_batches + minibatch_index
            
            # Perform the training of our convolution neural network.
            # Obtain the cost of each minibatch specified using the
            # minibatch_index.
            cost_ij = train_model(minibatch_index)
            
            if iter%20==0:
                statistics.saveParameters(params)
            if iter%20==0 and NCL>0:
                activations=get_activations()
                statistics.saveActivations(activations)
            
            # Save training error
            train_error.append(float(cost_ij))

            # Currently validation error depends on the type of task
            valid_losses = [valid_model(i) for i in range(n_valid_batches)]
            # Compute the mean prediction error across all the mini-batches.
            valid_score = np.mean(valid_losses)
            print("Iteration: "+str(iter+1)+"/"+str(num_epochs*n_train_batches)+", training cost: "+str(cost_ij)+", validation cost: "+str(valid_score))
                            
            if (iter%20==0):
                # Get predicted labels from validation set
                E = np.zeros((n_valid_batches*mini_batch_size,1))
                step=0
                for i in range(n_valid_batches):
                    buf = predict(i)
                    for j in range(mini_batch_size):
                        E[step,0]=buf[j]
                        step=step+1
                np.savetxt('output/E_pred_'+str(iter)+'.txt',E)

    test_losses = [test_model(i) for i in range(n_test_batches)]
    # Compute the mean prediction error across all the mini-batches.
    test_score = np.mean(test_losses)
    # Save validation error
    test_error = test_score
    print("Test error: "+str(test_error))

    statistics.writeActivations()
    # Return values:
    statistics.saveParameters(params)
    statistics.writeParameters()

 
