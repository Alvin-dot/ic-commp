from get_data import get_data_from_api
from datetime import datetime
from scipy import signal
import numpy as np
import pandas as pd
import time, sys, json

# Sampling rate given in Hz
data_freq = 5
# Set the data time window in minutes
data_time_window = int(sys.argv[2])
# Select PMU based on user input
pmu_select = sys.argv[1]

if pmu_select == 'eficiencia':
    pmu_select = 506
elif pmu_select == 'cabine':
    pmu_select = 515
elif pmu_select == 'patolina':
    pmu_select = 524
elif pmu_select == 'agrarias':
    pmu_select = 533

# Get time window from current time in unix milisseconds format
end_time_str = datetime.now()
end_time_unix = int(end_time_str.timestamp() * 1000)
start_time_unix = end_time_unix - (data_time_window * 60 * 1000)

# Get the frequency data based on the start and end time
api_data = get_data_from_api(start_time_unix, end_time_unix, feed_id=pmu_select, interval=data_freq,
                             interval_type=1, skip_missing=0)

unix_time_values = [i[0] for i in api_data]
frequency_values = [i[1] for i in api_data]

# Converts unix time to Numpy DateTime64 time milisseconds and converts from GMT time to local time
time_values = [np.datetime64(int(i - (3 * 3600000)), 'ms') for i in unix_time_values]

# Creates dataframe for variables
df = pd.DataFrame({"date": time_values, "original_freq": frequency_values})

# -----------------------------------
# Treatment of missing data
# -----------------------------------

# Replaces None values with NaN
df["original_freq"].fillna(np.NaN, inplace=True)

# -----------------------------------
# Treatment of outliers
# -----------------------------------

# Rolling mean + standard deviation method
roll_window = 20
alpha = 3

# Calculate moving average
df["roll_mean"] = df["original_freq"].rolling(window=roll_window).mean()

# Pad first 20 values with same as the original data
df.loc[:roll_window - 1, "roll_mean"] = df.loc[:roll_window - 1, "original_freq"]

# Defines constants used in for loop for better time performance
general_std = df["original_freq"].std()
outlier_counter = 0

for i in df["roll_mean"]:
    if not ((i + alpha * general_std) > df["original_freq"][outlier_counter] > (i - alpha * general_std)):
        df.loc[outlier_counter, "original_freq"] = np.NaN
    outlier_counter += 1

# -----------------------------------
# Interpolation process
# -----------------------------------

# Replaces NaN values with mean value
for i in range(len(df["original_freq"])):
    if df["original_freq"][i] != df["original_freq"][i]:
        df.loc[i, "original_freq"] = df["original_freq"].mean()


# -----------------------------------
# Removal of signal average
# -----------------------------------

df.loc[:, "freq"] = df.loc[:, "original_freq"]
df.loc[:, "freq"] -= df["original_freq"].mean()

# -----------------------------------
# Filtering
# -----------------------------------

# Application of a FIR bandpass filter
h = np.float32(signal.firwin(numtaps=2500, cutoff=(0.1, 2), window='hann', pass_zero='bandpass',
                             scale=False, fs=data_freq))

df["freq_filter"] = signal.filtfilt(h, 1, df["freq"])

# Take the signal derivative for detrending purposes
db = np.diff(df["freq_filter"], n=1)

# -----------------------------------
# FFT calculation
# -----------------------------------

# Uses Welch method for FFT calculation
fft_freq, fft_module = signal.welch(db, fs=data_freq, nperseg=(len(df["freq"])) // 20,
                                    average='mean', detrend='constant')

# -----------------------------------
# Data communication with PHP
# -----------------------------------

# Prepares dictionary for JSON file
data_to_php = {"freq": list(df['original_freq']),
			   "date": list(df['date'].astype(str)),
			   "welch": fft_module.tolist(),
			   "welch_freq": fft_freq.tolist()}

# Sends dict data to php files over JSON
print (json.dumps(data_to_php))