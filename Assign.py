import numpy as np
import scipy.stats as ss

#%%

### STEP 1 ###
# Converting LU suitability into a ranking for one LU type (whichever is the input)

def rank_array(array):
    # no need to flatten first, because ss.rankdata default flattens the array anyway
    ranks = ss.rankdata(-array, method = 'ordinal') 
        # Here (above), calculating rank of pixels 
        # Ordinal means pixels with same probability still given individual ranks
        # Using the negative of the array (multiplying by -1) means the ranks are highest to lowest (largest probability given rank '1')
    return(ranks) #gives the 1D array of pixel ranks

#%%
'''
Only select the top N ranks (N = number of required pixels for that LU type), rest becomes -1 (redefining their ranks as -1 so they're not used)
Input is 2D array, output is 1D.
Use the rank_array function (above)
'''
### STEP 2 ###
# Selecting only the required number of ranked pixels (according to previously-defined demand)

def Top_Rank(Array, N):
    ranks = rank_array(Array) #ranking the pixels largest to smallest, output 1D array
    TopRank = ranks.copy() #creating copy of ranks array
    TopRank[TopRank > N] = -1 #if rank higher than required pixel number, changed to -1
    return(TopRank)




#%%
'''
Remove all the conflicts by making the probability 0 in pixels where another
LU class has a higher rank (or higher priority in case of same rank).
Pay attention: input is (nrow,ncol) array, output is a (nrow*ncol,1) array!!
Use the Top_Rank function to recalculate the ranks in the while loop.
'''
#testing area

# Arable2D = prob_Arable 
# Pasture2D = prob_Pasture
# Forest2D = prob_Forest

# PaN = nr_Pasture
# FoN = nr_Forest
# ArN = nr_Arable

# np.amin(Arable_topranks)
# np.amax(Arable_topranks)

def Remove_Conflict(Arable2D, Forest2D, Pasture2D, ArN, FoN, PaN):

   
	# 1. flatten arrays to make calculations easier
    Arable1D = Arable2D.flatten()
    Forest1D = Forest2D.flatten()
    Pasture1D = Pasture2D.flatten()
    
    
	# 2. starting while loop and initiating an 'iterations' count
    iterations = 1
    while True:
        
		# 2.1/2.2 get the top ranks for each LU type using the flattened arrays                                                                                                     
        Arable_topranks = Top_Rank(Arable1D, ArN)
        Forest_topranks = Top_Rank(Forest1D, FoN)
        Pasture_topranks = Top_Rank(Pasture1D, PaN)

            
		# 2.3 for loop: 
        conflict = False
        for i in range(0, len(Arable1D)): #runs the for loop until it hits the length of the Arable1D array (all the pixels in the study area)
            #if one ranking higher (in practice, lower number = better ranking) than the other, make prob 0 in lower-ranking LU
            #if direct conflict with equal ranking, make probability 0 in the less important LU (chosen by user)
            
            if Arable_topranks[i] > 0 and Forest_topranks[i] > 0: #if the pixel has a rank in both Arable and Forest then...
                conflict = True # ... that means there is a conflict
                print(f"Arable + Forest conflict, pixel {i}")
                if Arable_topranks[i] <= Forest_topranks[i]:     #arable given more importance than forest (when equal, arable wins)
                    Forest1D[i] = 0
                    conflict = True
                    
                else:
                    Arable1D[i] = 0 #if forest ranked better than arable, arable assigned 0 (forest wins)
                    conflict = True
            
            if Arable_topranks[i] > 0 and Pasture_topranks[i] > 0:
                conflict = True 
                print(f"Arable + Pasture conflict, pixel {i}")
                if Arable_topranks[i] <= Pasture_topranks[i]:  #arable given more importance than pasture (when equal, arable wins)
                    Pasture1D[i] = 0
                    conflict = True
                else: 
                    Arable1D[i] = 0 #if pasture better ranked than arable, arable assigned 0 (pasture wins)
                    conflict = True
            
            if Pasture_topranks[i] > 0 and Forest_topranks[i] > 0:
                conflict = True 
                print(f"Pasture + Forest conflict, pixel {i}")
                if Pasture_topranks[i] <= Forest_topranks[i]:  #pasture given more importance than forest (when equal, pasture wins)
                    Forest1D[i] = 0
                    conflict = True
                else: 
                    Pasture1D[i] = 0
                    conflict = True #if forest better ranked than pasture, pasture given 0 (forest wins)    
            
    
                
		# 2.4 IF no conflicts, end the 'while' loop
        if conflict == False:
            print(f'Loop ended after {iterations} iterations, no further conflicts found ')
            break
                 #stops the while loop
		# ELSE IF conflict, restart 'while' loop with new LU probabilities (re-ranking etc)
        elif conflict == True:
            print(f'Conflict found on iteration {iterations}, restarting loop')
            iterations += 1  #adding 1 to the iterations count

            #should go back to start of while loop automatically now
            
    # Need to reshape back into 2D arrays, right now result is still 1D
    nrow, ncol = Arable2D.shape
    Arable_new = np.reshape(Arable1D, (nrow, ncol)) #reshaping back to 2D
    Forest_new = np.reshape(Forest1D, (nrow, ncol))
    Pasture_new = np.reshape(Pasture1D, (nrow, ncol))
    # 3.  export new LU probabilities  
    return(iterations, Arable_new, Forest_new, Pasture_new) #gives the number of iterations it needed, and the new 2D arrays of probabilities

#%%    
'''
Assign the LU. Inputs are the original 2D arrays with the LU probabilities and 
the required number of pixels, output is (nrow,ncol) array that represents LU
'''

def Assign_LU(Arable, Forest, Pasture, ArN, FoN, PaN):
    
    # 1. remove conflicts using the Remove_Conflict function
    iterations, Arable_new, Forest_new, Pasture_new = Remove_Conflict(Arable, Forest, Pasture, ArN, FoN, PaN) #output is the iterations and new probabilities
    #above output arrays are 2D
    
    nrow, ncol = Arable_new.shape #saving array dimensions
    
    # 2. Make one LU map combining the ranks of the three LU types
    
    #ranks with new (final) probabilites after being run through the Remove_Conflict function. 
    #each pixel will either have -1 (no ranking), 0 (another LU type had a higher ranking), or the actual ranking
    Arable_finalranks = Top_Rank(Arable_new, ArN)
    Forest_finalranks = Top_Rank(Forest_new, FoN)
    Pasture_finalranks = Top_Rank(Pasture_new, PaN)
    #above output is 1D arrays (been through the Top Rank function which flattens them)


    # Change the rank values to a unique value for each LU (1, 2, or 3 for A, P and F respectively)
    ar1= np.where(Arable_finalranks>0, 1, 0) # Where Arable_new array > 0 (where there is actually a rank), given value of 1, otherwise 0
    pa1= np.where(Pasture_finalranks>0, 2, 0) # Where Pasture_new array > 0, given value of 2, otherwise 0
    fo1= np.where(Forest_finalranks>0, 3, 0) # Where Forest_new array > 0, given value of 3, otherwise 0
    # Make one LU map by combining the ranks of the three LU types
    # Can add together because each pixel will only have one number (in the winning LU type) and the same pixel in the other LU type arrays will be 0
    Out = ar1+pa1+fo1

    Out = np.reshape(Out, (nrow,ncol)) #need to reshape to original dimensions of the input 
    
    return(Out)

# print(LU.shape)
# print(nrow, ncol) 



















