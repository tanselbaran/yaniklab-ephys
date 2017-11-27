"""
Added to GitHub on Tuesday, Aug 1st 2017

author: Tansel Baran Yasar

Containing the script for running through all recording sessions in the experiment for spike sorting or LFP analysis.

Usage: Recommended usage through the Jupyter notebooks for spike sorting or LFP analysis. For standalone usage,
run this script from bash as following:
    PATHEXP="/dir/to/the/folder/recording/subfolders/for/the/recording/sessions/"
    echo $PATHEXP|python analyze_all_recording_sessions.py
"""

from main import main
import pickle
import os
import sys

mainPath = sys.stdin.read().splitlines()[0] #Reads the mainPath from bash input.
dirs = os.listdir(mainPath)

for folder in (folder for folder in dirs if ((folder != 'log.txt') and (folder != 'notes.docx') and (folder != 'analyzed') and (folder != 'other'))):
    #Iterating over the folders for individual recording sessions, while skipping other files and folders.
    #All files/folders in the experiment folder that are not log, notes or analyzed should be grouped in a folder named 'other'
    print(mainPath + folder) #printing the recording session that is being analyzed
    p = pickle.load(open(mainPath + folder + '/paramsDict.p', 'rb')) #Loading the params_dict dictionary
    main(p) #Running the main function on the recording session.

print("Move on Buddy!")
