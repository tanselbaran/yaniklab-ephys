"""
Uploaded to GitHub on Tuesday, Aug 1st, 2017

author: Tansel Baran Yasar

Contains the code for analyzing the averages, amplitudes, standard errors
and temporal trends of the stimulus-evoked LFP response in the recording sessions
of an experiment.

Usage: Either run from the LFP analysis Jupyter notebook or standalone from Bash as following:
	PATHEXP="/path/to/the/folder/that/contains/the/individual/folders/for/all/recording/sessions/"
	echo $PATHEXP | python evoked_lfp_analysis.py
"""

import pickle
import os
import numpy as np
import math
from matplotlib.pyplot import *
from pandas import *

#Read the path to the folder containing all the recording sessions
mainPath = sys.stdin.read().splitlines()[0]
print(mainPath)
dirs = os.listdir(mainPath)

#Make a folder for the analysis results of the experiment
analyzed_path = mainPath + 'analyzed/'
if not os.path.exists(analyzed_path):
    os.mkdir(analyzed_path)
writer_0 = ExcelWriter(analyzed_path + 'peak_data_probe_0.xlsx', engine = 'xlsxwriter')
a=0

#Iterating through all recording sessions, while skipping the log and notes files, and 'analyzed' and 'other' folders
#Please add all the miscallaneous documents, pictures and folders in the 'other' folder
for folder in (folder for folder in dirs if ((folder != 'log.txt') and (folder != 'notes.docx') and (folder != 'analyzed') and (folder != 'other'))):
	p = pickle.load(open(mainPath + folder + '/paramsDict.p', 'rb'))
	if (p['probes'] == 2) and (a == 0):
	#Creating multiple sheets in the excel output if there are multiple probes
        writer_1 = ExcelWriter(analyzed_path + 'peak_data_probe_1.xlsx', engine = 'xlsxwriter')
    	a = a+1
	peak_info = {key: {} for key in range(p['probes'])}

	#Make folder for the analysis results of the recording session
	analyzed_path_for_folder = analyzed_path + folder
	if not os.path.exists(analyzed_path_for_folder):
		os.mkdir(analyzed_path_for_folder)

	for probe in range(p['probes']):
    	peak_info[probe]['peak_locs'], peak_info[probe]['peak_stds'], peak_info[probe]['peak_times'], peak_info[probe]['peak_errs'], peak_info[probe]['peak_amps'] = (np.zeros(p['nr_of_electrodes']) for i in range(5))
    	for shank in range(p['shanks']):
        	#Load the data for the shank
            data = pickle.load(open(mainPath + folder + '/probe_{:g}_shank_{:g}/probe_{:g}_shank_{:g}_evoked.pickle'.format(probe,shank,probe,shank), 'rb'))

            #Make folder for the analysis results of the shank
            analyzed_path_for_shank = analyzed_path_for_folder + '/probe_{:g}_shank_{:g}'.format(probe,shank)
            if not os.path.exists(analyzed_path_for_shank):
                os.mkdir(analyzed_path_for_shank)

            evoked = data['evoked'] #Evoked LFP waveforms
            evoked_avg = np.mean(evoked,0) #Average evoked LFP waveforms across trials
            evoked_std = np.std(evoked, 0) #Standard deviation of the evoked LFP waveforms across trials
            evoked_err = evoked_std / math.sqrt(len(evoked)) #Standard error of the evoked LFP waveforms across trials
            peak_info[probe]['peak_amps'][shank*p['nr_of_electrodes_per_shank']:(shank+1)*p['nr_of_electrodes_per_shank']] = np.min(evoked_avg, 1)
            time = np.linspace(-p['evoked_pre']*1000, p['evoked_post']*1000, (p['evoked_post'] + p['evoked_pre']) * p['sample_rate'])

			#Make a plot for the electrodes on the shank
            figure()
            y = np.linspace(0,800,8)
            pcolor(time,y,evoked_avg)
            colorbar()
            xlabel('Time(ms)')
            ylabel('Height from tip (um)')
            savefig(analyzed_path_for_shank+'/probe_{:g}_shank_{:g}_evoked.svg'.format(probe,shank), format = 'svg')
            close()

			#Calculate the peak parameters for each electrode and plot the average evoked LFP waveform for each electrode
            for trode in range(p['nr_of_electrodes_per_shank']):
                real_trode = p['nr_of_electrodes_per_shank']*shank + trode
                try:
                    peak_info[probe]['peak_locs'][real_trode] = np.where(evoked_avg[trode] == peak_info[probe]['peak_amps'][real_trode])[0]
                    peak_info[probe]['peak_stds'][real_trode] = evoked_std[trode][int(peak_info[probe]['peak_locs'][real_trode])]
                    peak_info[probe]['peak_errs'][real_trode] = evoked_err[trode][int(peak_info[probe]['peak_locs'][real_trode])]
                    peak_info[probe]['peak_times'][real_trode] = (peak_info[probe]['peak_locs'][real_trode] - p['evoked_pre']) / p['sample_rate']

                except ValueError:
                    pass

                figure()
                plot(time, evoked_avg[trode], 'k-')
                fill_between(time, evoked_avg[trode]-evoked_err[trode], evoked_avg[trode]+evoked_err[trode])
                xlabel('Time (ms)')
                ylabel('Voltage (uV)')
                savefig(analyzed_path_for_shank + '/electrode' + str(trode) + '_evoked.svg', format = 'svg')
                close()

    #Saving the peak parameters for each recording session into an excel file
    df0 = DataFrame({'Peak amplitudes': peak_info[0]['peak_amps'], 'Peak std': peak_info[0]['peak_stds'], 'Peak standard errors': peak_info[0]['peak_errs'], 'Peak times': peak_info[0]['peak_times']})
    df0.to_excel(writer_0, sheet_name = folder[0:30])
    if p['probes'] == 2:
        df1 = DataFrame({'Peak amplitudes': peak_info[1]['peak_amps'], 'Peak std': peak_info[1]['peak_stds'], 'Peak standard errors': peak_info[1]['peak_errs'], 'Peak times': peak_info[1]['peak_times']})
        df1.to_excel(writer_1, sheet_name = folder[0:30])

writer_0.save()
if p['probes'] == 2:
    writer_1.save()
