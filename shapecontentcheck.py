from gtpattern import *
import numpy as np

"""
Implementing the algorithm in triangularity lemma in Amri's book
"""

def contentshape_check(lmda, content):
    if(sum(lmda) != sum(content)): # check sizes
        return(False)
    dim = len(content) #size of the gtpattern
    matr = np.zeros((dim,dim)) #matrix to create a gtpattern
    matr[0,:len(lmda)] = lmda #setting the top row of the gtpattern
    a = np.array(matr[0]) #buffer array for the rows
    ind = dim-1
    
    for i in range(dim):
        if(a[i]==0):
            ind = i-1 #index of the last non-zero element of a.
            
    for i in range(1,dim):
        tmp = content[-i]
        j=ind
        while(tmp!=0):
            if((j==dim-1)):
                bo = 0
            else:
                bo = matr[i-1,j+1]
            if(tmp<=matr[i-1,j]-bo):
                a[j] = a[j]-tmp
                tmp = 0
            elif(j==0):
                return(False)
            else:
                tmp = tmp - (matr[i-1,j]-bo)
                a[j] = bo
                j=j-1
            
        matr[i] = a
        if(a[ind]==0):
            ind = ind -1

    return(gtpattern.from_matrix(matr))
