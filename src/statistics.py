import numpy as np
import theano
import theano.tensor as T
import hyppar

# Weights  and biases of 3 convlayers and on FC layer,
# to be saved during training
w1=[]
w2=[]
w3=[]
wf=[]
b1=[]
b2=[]
b3=[]
bf=[]

# Activations of the convlayers, to be saved during training
cl1_out = []
cl2_out = []
cl3_out = []

def writeParameters(dir="output"):
    global w1
    global b1
    global w2
    global b2
    global w3
    global b3
    global wf
    global bf

    ww1=np.zeros((len(w1),w1[0].shape[0],w1[0].shape[1],w1[0].shape[2],w1[0].shape[3]))
    ww2=np.zeros((len(w1),w2[0].shape[0],w2[0].shape[1],w2[0].shape[2],w2[0].shape[3]))
    ww3=np.zeros((len(w1),w3[0].shape[0],w3[0].shape[1],w3[0].shape[2],w2[0].shape[3]))
    wwf=np.zeros((len(w1),wf[0].shape[0],wf[0].shape[1]))
    for i in range(len(w1)):
        ww1[i,:,:,:]=w1[i]
        ww2[i,:,:,:]=w2[i]
        ww3[i,:,:,:]=w3[i]
        wwf[i]=wf[i]
        
    print(ww1.shape)
    np.save(dir+'/weights_convlayer1',ww1)
    np.save(dir+'/weights_convlayer2',ww2)
    np.save(dir+'/weights_convlayer3',ww3)
    np.save(dir+'/weights_FCC',wwf)

def writeActivations(dir="output"):
    global cl1_out
    global cl2_out
    global cl3_out

    
    print(cl1_out[0])

    ac1=np.zeros((len(cl1_out),cl1_out[0].shape[0],cl1_out[0].shape[1],cl1_out[0].shape[2]))
    ac2=np.zeros((len(cl1_out),cl2_out[0].shape[0],cl2_out[0].shape[1],cl2_out[0].shape[2]))
    ac3=np.zeros((len(cl1_out),cl3_out[0].shape[0],cl3_out[0].shape[1],cl3_out[0].shape[2]))
    for i in range(len(cl1_out)):
        ac1[i]=cl1_out[i]
        ac2[i]=cl2_out[i]
        ac3[i]=cl3_out[i]
    np.save(dir+"activations_convlayer1",ac1)
    np.save(dir+"activations_convlayer2",ac2)
    np.save(dir+"activations_convlayer3",ac3)

def saveActivations(cn_output):
    '''
    Completely saves the current activation tensors of
    the convolutional layers.
    '''
    global cl1_out
    global cl2_out
    global cl3_out

    activation1=np.array(cn_output[0][0,:])
    activation2=np.array(cn_output[1][0,:])
    activation3=np.array(cn_output[2][0,:])

    print(activation1)

    cl1_out.append(activation1)
    cl2_out.append(activation2)
    cl3_out.append(activation3)

def saveParameters(params):
    ''' 
    Takes a snapshot of all of the current weights and biases
    '''
    global w1 
    global b1
    global w2
    global b2
    global w3
    global b3
    global wf
    global bf

    for i in range(len(params)):
        if i==0:
            w1.append(params[i].get_value())
        elif i==1:
            b1.append(params[i].get_value())
        elif i==2:
            w2.append(params[i].get_value())
        elif i==3:
            b2.append(params[i].get_value())
        elif i==4:
            w3.append(params[i].get_value())
        elif i==5:
            b3.append(params[i].get_value())
        elif i==6:
            wf.append(params[i].get_value())
        elif i==7:
            bf.append(params[i].get_value())

    
