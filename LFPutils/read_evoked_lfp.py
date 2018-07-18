"""
Uploaded to Github on Tuesday, Aug 1st, 2017

author: Tansel Baran Yasar

Contains the function for reading the stimulus-evoked LFP for a recording session.

Usage: through the main function in main.py script
"""

from utils.filtering import *
from utils.reading_utils import *
from utils.load_intan_rhd_format import *
from matplotlib.pyplot import *
from utils.OpenEphys import *
from tqdm import tqdm
import pickle

def extract_stim_timestamps(stim):
    stim_timestamps = [] #numpy array that contains the stimulus timestamps
		#Saving the timestamps where digital input turns from 0 to 1
    for i in tqdm(range(1,len(stim))):
        if stim[i-1] == 0 and stim[i] != 1:
            stim_timestamps = np.append(stim_timestamps, i)
    stim_timestamps = np.asarray(stim_timestamps)
    return stim_timestamps

def extract_stim_timestamps_der(stim, p):
    stim_diff = np.diff(stim)
    stim_timestamps = np.where(stim_diff > 0)[0]

    #Cutting the triggers that happen too close to the beginning or the end of the recording session
    stim_timestamps = stim_timestamps[(stim_timestamps > (stim_timestamps[0] + p['cut_beginning']*p['sample_rate']))]
    stim_timestamps = stim_timestamps[(stim_timestamps < (stim_timestamps[-1]-p['cut_end']*p['sample_rate']))]
    return stim_timestamps

def read_evoked_lfp_from_stim_timestamps(filtered_data, stim_timestamps, p):
	#Saving the evoked LFP waveforms in an array
    evoked = np.zeros((len(stim_timestamps), len(filtered_data), int(p['sample_rate']*(p['evoked_pre']+p['evoked_post']))))
    for i in tqdm(range(len(stim_timestamps))):
        evoked[i,:,:] = filtered_data[:,int(stim_timestamps[i]-p['evoked_pre']*p['sample_rate']):int(stim_timestamps[i]+p['evoked_post']*p['sample_rate'])]
    return evoked

def read_evoked_lfp(probe,group,p,data):
    """This function processes the data traces for the specified probe and shank in a recording session to obtain
	the mean evoked LFP activity. It saves the evoked activity and the average evoked activity in a Pickle file. It
	supports the data from 'file per channel' (dat) and 'file per recording' (rhd) options of Intan software and the
	data recorded by Open Ephys software (cont).

        Inputs:
		coords: List including the coordinates of the shank or tetrode (either [height, shank] for tetrode configuration
			or [probe, shank] for linear configuration
            	p: Dictionary containing parameters (see main file)
		data: The numpy array that contains the data from either tetrode or shank in cases of tetrode or linear configurations
			respectively

        Outputs:
            Saves the evoked LFP waveforms in a numpy array (number of trigger events x number of electrodes per shank x number
		of samples in the evoked LFP window) and the time stamps of the stimulus trigger events in a pickle file saved in the folder
		for the particular probe and shank of the analysis.
    """
    print('#### Low-pass and notch filtering the data ####')

    nr_of_electrodes = p['nr_of_electrodes_per_group']
    save_file = p['path'] + '/probe_{:g}_group_{:g}/probe_{:g}_group_{:g}_evoked.pickle'.format(probe,group,probe,group)

    #Low pass filtering
    filt = lowpassFilter(rate = p['sample_rate'], high = p['low_pass_freq'], order = 3, axis = 1)
    filtered = filt(data)

    #Notch filtering
    if p['notch_filt_freq'] != 0:
        notchFilt = notchFilter(rate = p['sample_rate'], low = p['notch_filt_freq']-5, high = p['notch_filt_freq']+5, order = 3, axis = 1)
        filtered = notchFilt(filtered)

    #filtered = np.transpose(filtered)

    #Reading the trigger timestamps (process varies depending on the file format

    if p['fileformat'] == 'dat':
        trigger_filepath =  p['path'] + '/' + p['stim_file']
        with open(trigger_filepath, 'rb') as fid:
            trigger = np.fromfile(fid, np.int16)
        stim_timestamps = extract_stim_timestamps_der(trigger,p)

    elif p['fileformat'] == 'cont':
		#Reading the digital input from file
        trigger_filepath = p['path'] + '/all_channels.events'
        trigger_events = loadEvents(trigger_filepath)

        #Acquiring the timestamps of the ttl pulses
        timestamps = trigger_events['timestamps']
        eventId = trigger_events['eventId']
        eventType = trigger_events['eventType']
        channel = trigger_events['channel']

        timestamps_global = timestamps[eventType == 5]
        timestamps_ttl = []

        ttl_events = (eventType == 3)
        ttl_rise = (eventId == 1)

        for i in range(len(timestamps)):
            if (ttl_events[i]) and (ttl_rise[i]):
                timestamps_ttl = np.append(timestamps_ttl, timestamps[i])

        stim_timestamps = timestamps_ttl - timestamps_global[0]

    elif p['fileformat'] == 'rhd':
        trigger_all = []
        for file in range(len(p['rhd_file'])):
            data = read_data(p['path']+'/'+ p['rhd_file'][file])
            trigger = data['board_dig_in_data'][1]
            trigger_all = np.append(trigger_all, trigger)

        stim_timestamps = []
        for i in range(1,len(trigger_all)):
            if trigger_all[i-1] == 0 and trigger_all[i] == 1:
                stim_timestamps = np.append(stim_timestamps, i)

    evoked = read_evoked_lfp_from_stim_timestamps(filtered, stim_timestamps, p)
    #Save all evoked activity in a pickle file
    pickle.dump({'evoked':evoked, 'stim_timestamps':stim_timestamps}, open(save_file, 'wb'), protocol=-1)
