"""
Creation date: Tuesday, Aug 1st 2017

authors: Tansel Baran Yasar and Clemens Dlaska

Contains the functions that are used for creating the .prm and .prb files required for spike-sorting with Klustakwik, and running the Klustakwik on the tetrode or shank (for linear probes). 
"""

import numpy as np
import os as os
import h5py
from itertools import combinations
import json
import pickle
from scipy import signal
from shutil import copyfile
from utils.filtering import *

### Klustakwik utilities for tetrode data analyzing ###

def create_tetrode_prm_file(probe,h,s,p):
    """
    This function creates the .prm file required by Klustakwik for the analysis of the data from the tetrode located at shank s and height h.

    Inputs:
        probe: Index of the probe, for the recordings with multiple probes
        h: Height index of the tetrode (0 for the bottom-most tetrode)
        s: Shank index of the tetrode (0 for the left-most shank, looking at the electrode side)
        p: Parameters dictionary containing the parameters and preferences related to spike sorting.
    """

    file_dir = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)+'/tetrode_{:g}_{:g}.prm'.format(h,s)
    with open(file_dir, 'a') as text:
        print('experiment_name = \'tetrode_{:g}_{:g}\''.format(h,s), file = text)
        print('prb_file = \'tetrode_{:g}_{:g}.prb\''.format(h,s), file = text)
        print('traces = dict(raw_data_files=[experiment_name + \'.dat\'],voltage_gain=10., sample_rate =' + str(p['sample_rate']) + ', n_channels = 4, dtype = \'int16\')', file = text)

        print("spikedetekt = 'filter_low' : 500., \n 'filter_high_factor': 0.95 * .5, \n 'filter_butter_order': 3, \n #Data chunks. \n 'chunk_size_seconds': 1., \n 'chunk_overlap_seconds': .015, \n #Threshold \n 'n_excerpts': 50, \n 'excerpt_size_seconds': 1., \n 'use_single_threshold': True, \n 'threshold_strong_std_factor': 4.5 \n 'threshold_weak_std_factor': 2., \n 'detect_spikes': 'negative', \n # Connected components. \n 'connected_component_join_size': 1, \n #Spike extractions. \n 'extract_s_before': 10, \n 'extract_s_after': 10, \n 'weight_power': 2, \n #Features. \n 'n_features_per_channel': 3, \n 'pca_n_waveforms_max': 10000}", file = text)

        print('klustakwik2 = dict(prior_point=1, \n mua_point=2, \n noise_point=1, \n points_for_cluster_mask=100, \n penalty_k=0.0, \n penalty_k_log_n=1.0, \n max_iterations=1000, \n num_starting_clusters=500, \n use_noise_clusters=True, \n use_mua_cluster=True, \n num_changed_threshold=0.05, \n full_step_every=1, \n split_first=20, \n split_every=40, \n max_possible_clusters=1000, \n dist_thresh=log(10000.0), \n max_quick_step_candidates=100000000, \n max_quick_step_candidates_fraction=0.4, \n always_split_bimodal=False, \n subset_break_fraction=0.01, \n break_fraction=0.0, \n fast_split=False, \n max_split_iterations=None, \n consider_cluster_deletion=True, \n num_cpus=None)', file = text)

    text.close()

def create_tetrode_prb_file(probe,h,s,p):
    """
    This function creates the .prb file required by Klustakwik, which contains the electrode neighborhood and geometry information for the tetrode located at shank s and height h.

    Inputs:
        probe: Index of the probe, for the recordings with multiple probes
        h: Height index of the tetrode (0 for the bottom-most tetrode)
        s: Shank index of the tetrode (0 for the left-most shank, looking at the electrode side)
        p: Parameters dictionary containing the parameters and preferences related to spike sorting.
    """

    file_dir = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)+'/tetrode_{:g}_{:g}.prb'.format(h,s)
    tetrode = dict(channels = list(range(4)), graph = list(combinations(range(4),2)), geometry = {0: (0, 90), 1: (0, 60), 2: (0, 30), 3: (0, 0)})
    channel_groups = {0: tetrode}
    with open(file_dir, 'a') as text:
        print('channel_groups = {}'.format(channel_groups), file = text)

def do_klusta_for_tetrode(probe,h,s,p):
    """
    This function runs the klustakwik for the tetrode.

    Inputs:
        probe: Index of the probe, for the recordings with multiple probes
        h: Height index of the tetrode (0 for the bottom-most tetrode)
        s: Shank index of the tetrode (0 for the left-most shank, looking at the electrode side)
        p: Parameters dictionary containing the parameters and preferences related to spike sorting.
    """

    file_dir = p['path'] + '/tetrode_{:g}_{:g}'.format(h,s)
    os.chdir(file_dir)
    os.system('klusta tetrode_{:g}_{:g}.prm'.format(h,s))

### Klustakwik utilities for linear probe data analyzing ###

def create_shank_prm_file(probe,s,p):
    """
    This function creates the .prm file required by Klustakwik for the analysis of the data from the tetrode located at shank s and height h.

    Inputs:
        probe: Index of the probe, for recordings with multiple probes.
        s: Shank index (0 for the left-most shank, looking at the electrode side)
        p: Parameters dictionary containing the parameters and preferences related to spike sorting.
    """

    file_dir = p['path'] + '/probe_{:g}_shank_{:g}'.format(probe,s) + '/probe_{:g}_shank_{:g}.prm'.format(probe,s)
    if os.path.exists(file_dir):
        os.remove(file_dir)

    with open(file_dir, 'a') as text:
        print('experiment_name = \'probe_{:g}_shank_{:g}\''.format(probe,s), file = text)
        print('prb_file = \'probe_{:g}_shank_{:g}.prb\''.format(probe,s), file = text)
        print('traces = dict(raw_data_files=[experiment_name + \'.dat\'],voltage_gain=10., sample_rate =' + str(p['sample_rate']) + ', n_channels = ' + str(p['nr_of_electrodes']) + ', dtype = \'int16\')', file = text)

        print("spikedetekt = 'filter_low' : 500., \n 'filter_high_factor': 0.95 * .5, \n 'filter_butter_order': 3, \n #Data chunks. \n 'chunk_size_seconds': 1., \n 'chunk_overlap_seconds': .015, \n #Threshold \n 'n_excerpts': 50, \n 'excerpt_size_seconds': 1., \n 'use_single_threshold': True, \n 'threshold_strong_std_factor': 4.5 \n 'threshold_weak_std_factor': 2., \n 'detect_spikes': 'negative', \n # Connected components. \n 'connected_component_join_size': 1, \n #Spike extractions. \n 'extract_s_before': 10, \n 'extract_s_after': 10, \n 'weight_power': 2, \n #Features. \n 'n_features_per_channel': 3, \n 'pca_n_waveforms_max': 10000}", file = text)

        print('klustakwik2 = dict(prior_point=1, \n mua_point=2, \n noise_point=1, \n points_for_cluster_mask=100, \n penalty_k=0.0, \n penalty_k_log_n=1.0, \n max_iterations=1000, \n num_starting_clusters=500, \n use_noise_clusters=True, \n use_mua_cluster=True, \n num_changed_threshold=0.05, \n full_step_every=1, \n split_first=20, \n split_every=40, \n max_possible_clusters=1000, \n dist_thresh=log(10000.0), \n max_quick_step_candidates=100000000, \n max_quick_step_candidates_fraction=0.4, \n always_split_bimodal=False, \n subset_break_fraction=0.01, \n break_fraction=0.0, \n fast_split=False, \n max_split_iterations=None, \n consider_cluster_deletion=True, \n num_cpus=None)', file = text)

    text.close()

def create_shank_prb_file(probe,s,p):
    """
    This function copies the .prb file required by Klustakwik for the probe used in recording from the prb_files folder in the repository.

    Inputs:
        probe: Index of the probe, for recordings with multiple probes.
        s: Shank index (0 for the left-most shank, looking at the electrode side)
        p: Parameters dictionary containing the parameters and preferences related to spike sorting.
    """

    file_dir = p['path'] + '/probe_{:g}_shank_{:g}'.format(probe,s) + '/probe_{:g}_shank_{:g}.prb'.format(probe,s)
    os.getcwd()
    copyfile('../prb_files/' + p['probe_name'] + '.prb', file_dir)

def do_klusta_for_shank(probe,s,p):
    """
    This function runs the klustakwik for the shank. It creates a new folder for the shank first.

    Inputs:
        probe: Index of the probe, for recordings with multiple probes.
        s: Shank index (0 for the left-most shank, looking at the electrode side)
        p: Parameters dictionary containing the parameters and preferences related to spike sorting.
    """

    file_dir = p['path'] + '/probe_{:g}_shank_{:g}'.format(probe,s)
    os.chdir(file_dir)
    os.system('klusta probe_{:g}_shank_{:g}.prm'.format(probe,s))
