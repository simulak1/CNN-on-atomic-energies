import numpy as np
import random as rd
import matplotlib.pyplot as plt
import sys

ilayer=int(input("Which layer to plot(1=first)?\n"))-1
isample=int(input("Which sample to plot(1=first)?\n"))-1
A=np.load('activations_layer'+str(ilayer)+'_sample'+str(isample)+'.npy')
Niter=A.shape[0]
Nchannel=A.shape[1]
xdim=A.shape[3]
ydim=A.shape[3]
print("\n Loaded the activation tensor of convolutional layer "+str(ilayer+1)+" evaluated from rnd sample "+str(isample+1)+":")
print(" Number of saved iterations : "+str(Niter))
print(" Number of channels         : "+str(Nchannel))
print(" Dimension of the output    : ["+str(xdim)+","+str(ydim)+"]\n")
ind=1
ich=[]
while(ind>0):
    ind=int(input("Which channels to plot(-1:=all, 0:= enough)"))
    if(ind==-1):
        for i in range(Nchannel):
            ich.append(i)
    elif(ind>0):
        ich.append(ind-1)
    else:
        if(len(ich)==0):
            print("Give at least one channel.")
            continue
print("Printing channels "+str(ich))
Ncol=int(input("Give number of columns in the plot\n"))
Nrow=int(input("Give number of rows in the plot\n"))
plt.ion()
fig,ax=plt.subplots(Ncol,Nrow)

for i in range(Niter):
    count=0
    for j in range(Ncol):
        for k in range(Nrow):
            ax[j,k].clear()

    for j in range(Ncol):
        for k in range(Nrow):
            if(count<len(ich)):
                ax[j,k].imshow(A[i,count,:,:])
            count=count+1
    
    ax[0,0].set_title('Iteration '+str(i)+'/'+str(Niter))
    fig.canvas.draw()
    plt.pause(0.1)
