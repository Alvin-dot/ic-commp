#! /opt/ic-commp/bin/python3 startup.py

from get_data import get_data_from_api
from datetime import datetime
from scipy import signal
import numpy as np
import data_preprocessing as dpp
from sys import argv
from json import dumps
import math


def butterworth(data, cutoff, order, fs, kind="lowpass"):
    # highpass filter
    nyq = fs * 0.5

    cutoff = cutoff / nyq

    sos = signal.butter(order, cutoff, btype=kind, output="sos")

    filtrada = signal.sosfilt(sos, data)

    return filtrada


# Select PMU based on user input
pmuSelect = argv[1]
# Set the data time window in minutes
# Default value: 60
timeWindow = int(argv[2])
# Sampling rate in Hz
# Default value: 15
sampleRate = int(argv[3])
# Size of welch window in seconds
# Default value: 100
segmentWindow = int(argv[4])
# Overlap percentage of each segment
# Default value: 50
segmentOverlap = int(argv[5])
# Filter lower cutoff frequency
# Default value: 0.3
lower_filter = float(argv[6])
# Filter higher cutoff frequency
# Default value: 7.0
higher_filter = float(argv[7])
# Outlier detection constant
# Default value: 3.5
outlier_constant = float(argv[8])

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
apiData = np.array([get_data_from_api(
    startTime,
    endTime,
    feed_id=pmuSelect,
    interval=sampleRate,
    interval_type=1,
    skip_missing=0
)])

# Splits data into time and frequency values and removes missing data
unixValues = np.array([i[0] for i in apiData[0]])
freqValues = np.array([i[1] for i in apiData[0]], dtype=np.float64)

# Pads NaN with linear interpolation
# (this step is required for avoiding JSON parsing bug)
freqValues_toPHP = np.array([i[1] for i in apiData[0]], dtype=np.float64)
freqValues_toPHP = dpp.linear_interpolation(freqValues_toPHP)

# Checa se valores de frequência estão disponíveis
if (all(math.isnan(v) for v in freqValues)):
    raise NameError('Dados da PMU indisponíveis')

# Converts unix time to Numpy DateTime64 time milisseconds and converts from GMT time to local time
timeValues = np.array(
    [np.datetime64(int(i - (3 * 3600000)), 'ms') for i in unixValues])

ts = (timeValues[2] - timeValues[1]) / np.timedelta64(1, 's')
fs = round(1 / ts)

######################### WELCH CONFIG #########################

# Configure size of the Welch window in seconds and overlap percentage
numSeg = int(sampleRate * segmentWindow)
numOverlap = int(numSeg * (segmentOverlap/100))

######################### DATA PARCELING #########################

processedFreq, ts1, fs1 = dpp.preprocessamento(
    freqValues, 
    ts, 
    fs, 
    15, 
    lower_filter, 
    higher_filter, 
    outlier_constant
)

######################## WELCH CALCULATION #########################

# Welch Periodogram
welchFrequency, welchModule = signal.welch(
    processedFreq,
    fs=fs1,
    window="hann",
    nperseg=numSeg,
    noverlap=numOverlap,
    scaling="density",
    average="mean")

######################### DATA SEND #########################

# Prepares dictionary for JSON file
data_to_php = {
    "freq": freqValues_toPHP.tolist(),
    "date": timeValues.astype(str).tolist(),
    "welch": welchModule.tolist(),
    "welch_freq": welchFrequency.tolist()
}

# Adds advanced view type
data_to_php["freq_process"] = processedFreq.tolist()

# # Sends dict data to php files over JSON
print(dumps(data_to_php))
