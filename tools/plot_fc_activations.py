import numpy as np
import matplotlib.pyplot as plt
import sys

'''
A script tp plot FC activations. 

- Currently this probably works only for 0-dimensional data.
- First command line argument is the FC layer index, further 
  arguments specify which nodes to plot.
'''

# Ask for number of fclayers
Nlayers = int(input("How many fully connected layers?\n"))
while(Nlayers<0):
    Nlayers = int(input("Give a positive number\n"))
fclayer = int(input("Which layer is to be plotted? (1=first)\n"))-1
while(fclayer<0 or fclayer>Nlayers-1):
    fclayer = int(input("Do better.\n"))-1
if(Nlayers==fclayer+1):
    ptd= int(input("Plot against the true distribution (0=NO, 1=YES)?\n"))
    while(ptd<0 or ptd>1):
        ptd= int(input("Plot against the true distribution (0=NO, 1=YES)?\n"))
    if(ptd==1):
        plot_true_dist=True
        Xdata=np.load('validation_features.npy')
        Ydata=np.load('validation_targets.npy')
    else:
        plot_true_dist=False
else:
    plot_true_dist=False
plot_period=int(input("How many iterations to skip between plots?\n"))+1
while(plot_period<1):
    plot_period=int(input("Skip more lines\n"))+1
A0 = np.load('activations_fclayer'+str(fclayer)+'.npy')
# Specify which nodes to plot
nodes=[]
nod=1
while(nod>0):
    nod=int(input("Add a node to plot(0: no more, -1: all):\n"))
    if(nod==-1):
        nodes=np.arange(len(A0[0,:,0]))
    elif(nod>0):
        nodes.append(nod-1)

print(A0.shape)
Niter=len(A0)
Nnodes=len(nodes)
plt.ion()
fig,ax=plt.subplots(1)

for i in range(Niter):
    if(i%plot_period==0):
        ax.clear()
        ax.set_title('Iteration '+str(i)+'/'+str(Niter))
        for j in range(Nnodes):
            ax.plot(A0[i,nodes[j],:],'b-')
        if(plot_true_dist):ax.plot(Ydata[:,0],'r-')
        fig.canvas.draw()
        plt.pause(0.0002)
    
