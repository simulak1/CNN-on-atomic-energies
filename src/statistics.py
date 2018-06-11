import numpy as np
import theano
import theano.tensor as T
import hyppar

# Weights  and biases of 3 convlayers and on FC layer,
# to be saved during training
wcl=[]
bcl=[]
wfc=[]
bfc=[]


# Activations of the convlayers, to be saved during training
conv_out = []
fc_out   = []

def saveAll():
    '''
    Writes everything there is to output file.
    '''
    global wfc
    global bfc
    global wcl
    global bcl

    writecl=len(wcl)>1 # Plot convlayer parameters
    writefc=len(wfc)>1 # Plot fclayer parameters
    
    if (writecl) : writeClParameters()
    if (writefc) : writeFcParameters()
    #if(hyppar.NFC>0):writefcActivations()
    
def writeClParameters(dir="Statistics"):
    '''
    - Writes convolutional layer parameters into npy-files.
    - Every simulation containing CL layers includes at least
      parameters from two iterations: the initial weights, and weights
      after first gradient jump.
    - Writes all layers and corresponding biases and weights in their own files. 
    '''
    global wcl
    global bcl

    # Use: hyppar module
    Nl           = hyppar.NCL
    Nc           = hyppar.Nchannel
    filter       = hyppar.filter
    image_spec_x = hyppar.image_spec_x
    image_spec_y = hyppar.image_spec_y

    # Number of saved snapshots
    Niter = len(wcl)

    for i in range(Nl):
        wim = np.zeros((Niter,Nc[i+1],Nc[i],filter[i][0],filter[i][1]))
        bim = np.zeros((Niter,Nc[i+1]))
        for j in range(Niter):
            wim[i,:,:,:,:] = wcl[j][i]
            bim[i,:]       = bcl[j][i]
        np.save(hyppar.current_dir+'/'+dir+'/weights_convlayer_'+str(i),wim)
        np.save(hyppar.current_dir+'/'+dir+'/biases_convlayer_'+str(i),bim)
    
    
def writeFcParameters(dir="Statistics"):
    '''
    Just as writeClParameters, but for FC layers.
    '''
    global wfc
    global bfc

    # Use: hyppar module
    NFC          = hyppar.NFC
    Nl           = hyppar.NCL
    Nc           = hyppar.Nchannel
    image_spec_x = hyppar.image_spec_x
    image_spec_y = hyppar.image_spec_y
    fc_out       = hyppar.fc_out
    
    # Derived variables
    Niter   = len(wfc)
    
    if(Nl>0):
        num_in = Nc[Nl]*image_spec_x[-1]*image_spec_y[-1]
    else:
        num_in = image_spec_x[0]*image_spec_y[0]



    for i in range(NFC):
        num_out=fc_out[i]
        
        wim=np.zeros((Niter,num_in,num_out))
        for j in range(Niter):
            wim[j,:,:]=wfc[j][i]
        bim=np.zeros((Niter,num_out))
        for j in range(Niter):
            bim[j,:]=bfc[j][i]
        np.save(hyppar.current_dir+'/'+dir+'/weights_fclayer'+str(i),wim)
        np.save(hyppar.current_dir+'/'+dir+'/biases_fclayer'+str(i),bim)

        num_in=num_out
        


def writeActivations(dir="Statistics"):
    global conv_out

    # Use: hyppar module
    Nl           = hyppar.NCL
    Nc           = hyppar.Nchannel
    image_spec_x = hyppar.image_spec_x
    image_spec_y = hyppar.image_spec_y

    # Derived variables
    Niter   = len(conv_out)
    Nsample = len(conv_out[0])
    
    for i in range(Nl):
        for j in range(Nsample):
            image = np.zeros((Niter,Nc[i+1],image_spec_x[i+1], image_spec_y[i+1]))
            for k in range(Niter):
                image[k,:,:,:] = conv_out[k][j][i] 
            np.save(hyppar.current_dir+'/'+dir+'/activations_layer'+str(i)+'_sample'+str(j),image)
        
def writefcActivations(dir="Statistics"):
    global fc_out
    NFC = hyppar.NFC

    Niter = len(fc_out)
    Nlayer = len(fc_out[0])
    Nsample = hyppar.Nsamples_fc

    for i in range(NFC):
        Nnode=hyppar.fc_out[i]
        image = np.zeros((Niter,Nnode,Nsample))
        for j in range(Nnode):
            for k in range(Niter):
                image[k,j,:] = fc_out[k][i][j]
        np.save(hyppar.current_dir+'/'+dir+'/activations_fclayer'+str(i),image)

            
def saveActivations(activations):
    '''
    Completely saves the current activation tensors of
    the convolutional layers from 2 random input samples.

    Data structure for saved activations:
    conv_out   : #iter x [#samples x [#Layers x #channels x xdim x ydim]]
   
    Example: 
    iter i, sample s, layer l has a numpy entry obtained by
    conv_out[i][s][l] := Nlayers X xdim X ydim
    '''
    global conv_out

    iter=[] # Conv_out elements

    sample1=[] # iter elements
    sample2=[]

    for i in range(len(activations)):
        A1=np.array(activations[i][0]) # layer i, sample 1
        A2=np.array(activations[i][1]) # layer i, sample 2
        sample1.append(A1)
        sample2.append(A2)#

    iter.append(sample1)
    iter.append(sample2)
    
    conv_out.append(iter)
    
def savefcActivations(activations):
    '''
    Completely saves the current activation tensors of 
    the fully connected layers from input samples. 
    Data structure for saved activations: 
    fc_out   : #iter x [#layers x [#samples  x #nodes]] 
    Example: 
    iter i, layer l, node n has a numpy entry obtained by 
    fc_out[i][l][n] := Nsamples
    '''
    global fc_out

    Nl = len(activations)
    Ns = hyppar.Nsamples_fc

    
    iter=[] # fc_out snapshot
    
    for i in range(Nl):              # Layer
        layer = []
        A = np.array(activations[i])
        for j in range(hyppar.fc_out[i]):   # Node
            node = []
            for k in range(Ns):      # feature
                node.append(A[k,j])
            layer.append(node)
        iter.append(layer)
            
    fc_out.append(iter)

def saveParameters(params):
    ''' 
    Takes a snapshot of all of the current weights and biases
    
    Input  : An array of length 2 x (NCL+NFC) including convlayer
            and fclayer weights and biases.
    Output  
    - snapwcl : an array of shape NCL x [hyppar.filter]. (Array of NCL filters)
    - snapbcl : Array with NCL elements, which are arrays of length Nchannels.
    - snapwfc : an array of shape NFC x [fc_out[i-1] x fc_out[i]].
    - snapbfc : array of NFC elements, which are arrays of lenght fc_out[i].
    
    These snapshots are added to the end of the global arrays called below.
    
    '''
    global wfc
    global bfc
    global wcl
    global bcl


    snapwcl = []
    snapbcl = []
    snapwfc = []
    snapbfc = []

    for layer in range(hyppar.NCL): # ConvLayers
        i= 2*layer
        snapwcl.append(params[i].get_value())
        snapbcl.append(params[i+1].get_value())
    for layer in range(hyppar.NCL,hyppar.NCL+hyppar.NFC): # FClayers
        i=2*layer
        snapwfc.append(params[i].get_value())
        snapbfc.append(params[i+1].get_value())
            
    wcl.append(snapwcl)
    bcl.append(snapbcl)
    wfc.append(snapwfc)
    bfc.append(snapbfc)

    
