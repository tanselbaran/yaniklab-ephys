"""
Uploaded on GitHub on Tuesday, Aug 1st, 2017

author: Tansel Baran Yasar

Contains the information and the maps for the Neuronexus probes that are used in the lab.
"""

import numpy as np

def load_probe_info(probe):
    """
    This function generates a dictionary containing the information about the probe used in the experiment.

    Inputs:
        probe: String indicating the model of the probe.

    Outputs:
        probe_info: Dictionary including the information about the probe. The dictionary must include the following keys:
            'numShanks' : Number of shanks
            'type': Configuration of the electrodes (tetrode, linear, polytrode)
            'numTetrodes': Total number of tetrodes on the probe (only for tetrode configuration)
            'numTetrodesPerShank': Number of tetrodes on each shank (only for tetrode configuration)
            'numTrodesPerShank': Number of electrodes on each shank (only for linear configuration)
            'numTrodes': Total number of electrodes on the probe (only for linear configuration)
            'id': For tetrode configuration, (numTetrodesPerShank) x (numShanks) x 4; for linear   configuration, (numShanks) x (numTrodesPershank) Numpy array
        containing how the physical mapping of the probe corresponds to the mapping of the electrodes on Intan. When generating this list, please use the following
        convention: Shanks are numbered from 0, starting from the left. Tetrodes or the electrodes of a linear probe are numbered from 0, starting from bottom of the
        shank. Electrodes in a tetrode are numbered from 0, starting from the left-most electrode and continuing counter clockwise. Please do not forget that the
        channel numbers on Intan software start from 0.
    """
    probe_info = {}
    probe_info['name'] = probe

    if probe == 'a4x4_tet_150_200_121':
        probe_info['numShanks'] = 4
        probe_info['type'] = 'tetrode'
        probe_info['numTetrodes'] = 16
        probe_info['numTetrodesPerShank'] = 4

        ###Channel mapping###
        neuronexus_to_intan =[17,21,42,25,38,27,19,34,23,32,36,49,29,51,31,53,48,55,50,57,52,60,54,62,56,58,63,61,59,44,46,40,22,16,18,5,3,1,4,6,0,8,2,10,7,12,9,14,11,33,13,35,15,26,30,41,28,45,37,24,39,20,43,47]
        id = np.zeros((probe_info['numShanks'],probe_info['numTetrodesPerShank'],4))
        for i in range(probe_info['numShanks']):
            id[0,i,:] = [neuronexus_to_intan[0+i*16],neuronexus_to_intan[2+i*16],neuronexus_to_intan[15+i*16],neuronexus_to_intan[13+i*16]]
            id[1,i,:] = [neuronexus_to_intan[1+i*16],neuronexus_to_intan[4+i*16],neuronexus_to_intan[14+i*16],neuronexus_to_intan[10+i*16]]
            id[2,i,:] = [neuronexus_to_intan[3+i*16],neuronexus_to_intan[6+i*16],neuronexus_to_intan[12+i*16],neuronexus_to_intan[9+i*16]]
            id[3,i,:] = [neuronexus_to_intan[5+i*16],neuronexus_to_intan[7+i*16],neuronexus_to_intan[11+i*16],neuronexus_to_intan[8+i*16]]

        probe_info['id'] = id

    elif probe == 'a4x8_5mm_100_200_177':
        probe_info['numShanks'] = 4
        probe_info['type'] = 'linear'
        probe_info['numTrodesPerShank'] = 8
        probe_info['numTrodes'] = 32

        ###Channel mapping###
        neuronexus_to_intan = [15,5,4,14,3,6,2,7,1,8,0,9,13,12,11,10,21,20,19,18,22,24,23,17,25,16,26,28,27,30,29,31]
        id = np.zeros((probe_info['numTrodesPerShank'], probe_info['numShanks'],))
        for i in range(probe_info['numShanks']):
            id[:,i] = [neuronexus_to_intan[0+i*8], neuronexus_to_intan[7+i*8], neuronexus_to_intan[1+i*8], neuronexus_to_intan[6+i*8], neuronexus_to_intan[2+i*8], neuronexus_to_intan[5+i*8], neuronexus_to_intan[3+i*8], neuronexus_to_intan[4+i*8]]

        probe_info['id'] = id

        #2X16 linear probe  a2x16_10mm_100_500_177
    elif probe == 'a2x16_10mm_100_500_177':
        probe_info['numShanks'] = 2
        probe_info['type'] = 'linear'
        probe_info['numTrodesPerShank'] = 16
        probe_info['numTrodes'] = 32

        ###Channel mapping###
        neuronexus_to_intan = [30,26,21,17,27,22,20,25,28,23,19,24,29,18,31,16,0,15,2,13,8,9,7,1,6,14,10,11,5,12,4,3]
        id = np.zeros((probe_info['numTrodesPerShank'], probe_info['numShanks'],))
        for i in range(probe_info['numShanks']):
            id[:,i] = [neuronexus_to_intan[0+i*16], neuronexus_to_intan[15+i*16], neuronexus_to_intan[1+i*16], neuronexus_to_intan[14+i*16], neuronexus_to_intan[2+i*16], neuronexus_to_intan[13+i*16], neuronexus_to_intan[3+i*16], neuronexus_to_intan[12+i*16], neuronexus_to_intan[4+i*16], neuronexus_to_intan[11+i*16], neuronexus_to_intan[5+i*16], neuronexus_to_intan[10+i*16], neuronexus_to_intan[6+i*16], neuronexus_to_intan[9+i*16], neuronexus_to_intan[7+i*16], neuronexus_to_intan[8+i*16]]

        probe_info['id'] = id

    return probe_info
