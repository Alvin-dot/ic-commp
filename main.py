from get_data import get_data_from_api
from signal_processing import get_frequency_fft
from datetime import datetime
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from scipy import signal, stats

# Get start and end time
start_time_str = datetime.strptime('07.11.2020 06:00:00', '%d.%m.%Y %H:%M:%S')
start_time_unix = start_time_str.timestamp() * 1000

end_time_str = datetime.strptime('07.11.2020 08:00:00', '%d.%m.%Y %H:%M:%S')
end_time_unix = end_time_str.timestamp() * 1000

# Frequency value derived from 4.1.5 downsampling
data_freq = 5

# Get the frequency data based on the start and end time
api_data = get_data_from_api(start_time_unix, end_time_unix, interval=data_freq, interval_type=1, skip_missing=0)

# Converts unix time from GMT time to local time and removes milisseconds
unix_time_values = [(i[0] - (3 * 3600000)) / 1000 for i in api_data]
frequency_values = [i[1] for i in api_data]

# Converts unix time to Numpy DateTime64 time
time_values = [np.datetime64(int(i), 's') for i in unix_time_values]

# Creates dataframe for variables
df = pd.DataFrame({"freq": frequency_values, "date": time_values, "original_freq": frequency_values})

# -----------------------------------
# Treatment of missing data
# -----------------------------------

# Replaces None values with NaN
none_counter = 0
for i in df["freq"]:
    if i is None:
        df["freq"][none_counter] = np.NaN
    none_counter += 1

# -----------------------------------
# Treatment of outliers
# -----------------------------------

# ROLLING MEAN AND STANDARD DEVIATION METHOD
roll_window = 20
alpha = 3

# Calculate moving average
df["roll_mean"] = df.freq.rolling(window=roll_window).mean()

# Pad first 20 values with same as the original data
df.loc[:roll_window-1, "roll_mean"] = df.loc[:roll_window-1, "freq"]

for i in range(len(df["roll_mean"])):
    if not ((abs(df["roll_mean"][i]) + alpha * df.freq.std()) > abs(df.freq[i]) > (abs(df["roll_mean"][i]) - alpha * df.freq.std())):
        df.loc[i, "freq"] = np.NaN

'''
# Z SCORE METHOD
z_score_counter = 0

df["z_score"] = stats.zscore(df["freq"])

for i in df["z_score"]:
    if i >= 3 or i <= -3:
        df.loc[z_score_counter, "freq"] = np.NaN
    z_score_counter += 1
'''
# -----------------------------------
# Interpolation process
# -----------------------------------
# Replaces NaN values with EWM data smoothing filter
ewm_counter = 0

df["ewm"] = df["freq"].ewm(alpha=0.3).mean()

for i in df["freq"]:
    if i != i:
        df.loc[ewm_counter, "freq"] = df.loc[ewm_counter, "ewm"]
    ewm_counter += 1

# -----------------------------------
# Removal of signal average
# -----------------------------------
df.loc[:, "freq_no_avg"] = df.loc[:, "freq"] - np.mean(df["freq"])

# -----------------------------------
# Filtering
# -----------------------------------

h = np.float32(signal.firwin(numtaps=500, cutoff=[0.25, 2.4], window='hann', pass_zero='bandpass', scale=False, fs=data_freq))
df["freq_filter"] = signal.lfilter(h, 1, df["freq_no_avg"])

# -----------------------------------
# FFT calculation
# -----------------------------------
fft_module, fft_freq, fft_angle = get_frequency_fft(df["freq_filter"], data_freq)
# fft_freq, fft_module = signal.welch(df["freq_filter"], fs=data_freq)

# -----------------------------------
# Plotting
# -----------------------------------

'''
fig = go.Figure()
fig.add_trace(go.Scatter(x=time_values, y=df["freq_no_avg"], mode='markers', name='original'))
fig.add_trace(go.Scatter(x=time_values, y=df["freq_filter"], mode='markers', name='filtered'))
fig.show()
'''
fig = go.Figure()
fig.add_trace(go.Scatter(x=fft_freq, y=fft_module, mode='markers'))
fig.show()
