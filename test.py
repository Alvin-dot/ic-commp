from get_data import get_data_from_api
from datetime import datetime
from scipy import signal
import numpy as np
import data_preprocessing as dpp
import sys
import json
import time

import matplotlib.pyplot as plt

print("Program starting...")

# Sampling rate in Hz
sampleRate = 5

# Set the data time window in minutes
timeWindow = 60

# Select PMU based on user input
pmuSelect = "agrarias"

if pmuSelect == "eficiencia":
    pmuSelect = 506
elif pmuSelect == "cabine":
    pmuSelect = 515
elif pmuSelect == "palotina":
    pmuSelect = 524
elif pmuSelect == "agrarias":
    pmuSelect = 533

######################### DATE CONFIGURATION #########################

# Get time window from current time in unix milisseconds format
endTime = datetime.now()
endTime = int((endTime.timestamp() - 60) * 1000)
startTime = endTime - (timeWindow * 60 * 1000)

######################### DATA AQUISITION #########################

# Get the frequency data based on the start and end time
apiData = np.array([get_data_from_api(startTime,
                                      endTime,
                                      feed_id=pmuSelect,
                                      interval=sampleRate,
                                      interval_type=1,
                                      skip_missing=0)])

# Splits data into time and frequency values and removes missing data
unixValues = np.array([i[0] for i in apiData[0]])
freqValues = np.array([i[1] for i in apiData[0]], dtype=np.float64)
freqValues_toPHP = np.array([i[1] for i in apiData[0]], dtype=np.float64)

# Converts unix time to Numpy DateTime64 time milisseconds and converts from GMT time to local time
timeValues = np.array(
    [np.datetime64(int(i - (3 * 3600000)), 'ms') for i in unixValues])

######################### FILTER DESIGN #########################

# FIR highpass filter coefficient design
highpassFreq = 0.15
hpCoef = np.float32(signal.firwin(numtaps=999,
                                  cutoff=highpassFreq,
                                  window='hann',
                                  pass_zero='highpass',
                                  fs=sampleRate))

######################### WELCH CONFIG #########################

# Configure size of the Welch window in seconds and overlap percentage
windowTime = 100
overlapPercentage = 0.50

numSeg = int(sampleRate * windowTime)
numOverlap = int(numSeg * overlapPercentage)

######################### PARCEL CONFIG #########################

# Set size of data blocks in minutes
numberBlocks = timeWindow / 20

# Corrects length of frequency list
if len(freqValues) % numberBlocks != 0:
    exactMult = np.floor(len(freqValues) / numberBlocks)
    exactLen = int(exactMult * numberBlocks)
    lenDiff = len(freqValues) - exactLen
    freqValues = freqValues[:-lenDiff]

# Instantiate list for output values
processedFreq = np.array([])

######################### DATA PARCELING #########################

for dataBlock in np.array_split(freqValues, numberBlocks):

    # Check for long NaN runs
    nanRun = dpp.find_nan_run(dataBlock, run_max=10)

    # Linear interpolation
    dataBlock = dpp.linear_interpolation(dataBlock)

    # Detrend
    dataBlock -= np.nanmean(dataBlock)

    # HP filter
    dataBlock = signal.filtfilt(hpCoef, 1, dataBlock)

    # Outlier removal
    dataBlock = dpp.mean_outlier_removal(dataBlock, k=3.5)

    # Linear interpolation
    dataBlock = dpp.linear_interpolation(dataBlock)

    processedFreq = np.append(processedFreq, dataBlock)

######################## WELCH CALCULATION #########################

# Welch Periodogram
welchFrequency, welchModule = signal.welch(processedFreq,
                                           fs=sampleRate,
                                           window="hann",
                                           nperseg=numSeg,
                                           noverlap=numOverlap,
                                           scaling="density",
                                           average="mean")

######################### DATA SEND #########################
plt.plot(welchFrequency, welchModule)
plt.show()
