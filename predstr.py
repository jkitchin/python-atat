#!/usr/bin/env python

'''
fit.out
Contains the results of the fit, one structure per line and
each line has the following information:

  concentration energy fitted_energy (energy-fitted_energy) weight index

'concentration' lies between 0 and 1.
'energy' is per site (a site is a place where more than one atom type can lie)
'weight' is the weight of this structure in the fit.
'index' is the name of the directory associated with this structure.


predstr.out
Contains the predicted energy (per site) of all structures
maps has in memory but whose true energy is unknown or has been
flagged with error.  Format: one structure per line, and each line has
the following information:

  concentration energy predicted_energy index status

index is the structure number (or -1 if not written to disk yet).
energy is the calculated energy (or 0 if unknown).
status is either

  b for busy (being calculated),
  e for error or
  u for unknown (not yet calculated).
  A g is appended to status if that structure is predicted to be a ground state.

To list all predicted ground states, type grep 'g' predstr.out
'''

def GetPredictedEnergies(predstrfile='predstr.out'):

    f = open(predstrfile,'r')

    pred_dict = {}
    x_dict = {}

    for line in f:
        x,energy,predicted_energy,index,status = line.split()
        '''
        for some reason some indices have ? instead of the structure
        number. i think that means they are uncalculated and are
        from the direct enumeration
        '''

        if  index != '?':
            pred_dict[int(index)] = float(predicted_energy)
            x_dict[int(index)] = float(x)

    f.close()

    return x_dict,pred_dict

def GetFittedEnergies(fitfile='fit.out'):

    f = open(fitfile,'r')

    dict = {}
    x_dict = {}

    for line in f:
        x,energy,predicted_energy,error,weight,index = line.split()
        dict[int(index)] = float(predicted_energy)
        x_dict[int(index)] = float(x)



    f.close()

    return x_dict,dict

class Container:
    def __init__(self):
        pass

def ParseFit(fitfile='fit.out'):

    dict = {}

    f = open(fitfile,'r')
    for line in f:
        x,energy,predicted_energy,error,weight,index = line.split()

        c = Container()
        c.composition = float(x)
        c.energy = float(energy)
        c.predicted_energy = float(predicted_energy)

        dict[int(index)] = c

    f.close()

    return dict

def ParsePredstr(predstrfile='predstr.out'):

    f = open(predstrfile,'r')

    dict = {}

    for line in f:
        x,energy,predicted_energy,index,status = line.split()


        if  index != '?':

            c = Container()
            c.composition = float(x)
            c.predicted_energy = float(predicted_energy)
            dict[int(index)] = c

    f.close()

    return dict
