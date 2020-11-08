from get_data import get_data_from_api
from signal_processing import get_frequency_fft
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from scipy import signal, stats

# Get start and end time
start_time_str = datetime.strptime('07.11.2020 16:00:00', '%d.%m.%Y %H:%M:%S')
start_time_unix = start_time_str.timestamp() * 1000

end_time_str = datetime.strptime('07.11.2020 17:00:00', '%d.%m.%Y %H:%M:%S')
end_time_unix = end_time_str.timestamp() * 1000

# Frequency value derived from 4.1.5 downsampling
data_freq = 5

# Get the frequency data based on the start and end time
api_data = get_data_from_api(start_time_unix, end_time_unix, interval=data_freq, interval_type=1, skip_missing=1)

# Converts unix time from GMT time to local time and removes milisseconds
unix_time_values = [(i[0] - (3 * 3600000)) / 1000 for i in api_data]
frequency_values = [i[1] for i in api_data]

# Converts unix time to Numpy DateTime64 time
time_values = [np.datetime64(int(i), 's') for i in unix_time_values]

# -----------------------------------
# Treatment of missing data
# -----------------------------------

# Replaces None values with NaN
none_counter = 0
none_flag = False
for i in frequency_values:
    if i is None:
        frequency_values[none_counter] = np.NaN
        none_flag = True
    none_counter += 1

# Interpolates missing data
# CONFIRMAR PARÂMETROS DE METHOD E LIMIT FUTURAMENTE COM PROFESSOR
df = pd.DataFrame({"freq": frequency_values, "date": time_values})
if none_flag:
    df["freq"].interpolate(method='nearest', limit=10, limit_area='inside', inplace=True)

# -----------------------------------
# Treatment of outliers
# -----------------------------------
'''
# ROLLING MEAN AND STANDARD DEVIATION METHOD
roll_window = 20
alpha = 3

# Calculate moving average
df["roll_mean"] = df.freq.rolling(window=roll_window).mean()

# Pad first 20 values with same as the original data
df.loc[:roll_window-1, "roll_mean"] = df.loc[:roll_window-1, "freq"]

for i in range(len(df["roll_mean"])):
    if (abs(df["roll_mean"][i]) + alpha * df.freq.std()) > abs(df.freq[i]) > (abs(df["roll_mean"][i]) - alpha * df.freq.std()):
        df.loc[i, "freq_roll"] = df.loc[i, "freq"]
    else:
        df.loc[i, "freq_roll"] = np.NaN
        print("heyhey")
'''

'''
# Z SCORE AND EWM METHOD
z_score_counter = 0

df["z_score"] = stats.zscore(df["freq"])
df["ewm"] = df["freq"].ewm(alpha=0.3).mean()
df["freq_ewm"] = df["freq"]

for i in df["z_score"]:
    if i >= 3 or i <= -3:
        df.loc[z_score_counter, "freq_ewm"] = df.loc[z_score_counter, "ewm"]
    z_score_counter += 1

fig = go.Figure()
fig.add_trace(go.Scatter(x=time_values, y=df["freq"], mode='markers', name='original'))
fig.add_trace(go.Scatter(x=time_values, y=df["freq_ewm"], mode='markers', name='filtered'))
fig.show()

fig = go.Figure()
fig.add_trace(go.Scatter(x=time_values, y=(df["freq"] - df["freq_ewm"]), mode='markers', name='filtered'))
fig.show()
'''

'''
# -----------------------------------
# 4.1.3 Removal of signal average
# -----------------------------------
# freq_roll_output = freq_roll_output - np.mean(freq_roll_output)
freq_roll_output = frequency_values - np.mean(frequency_values)

# -----------------------------------
# 4.1.4 Filtering
# -----------------------------------
h = np.float32(signal.firwin(numtaps=500, cutoff=[0.1, 2], pass_zero='bandpass', scale=True, fs=data_freq))
filtered_freq = signal.lfilter(h, 1, freq_roll_output)

# -----------------------------------
# FFT calculation
# -----------------------------------
fft_module, fft_freq, fft_angle = get_frequency_fft(filtered_freq, data_freq)


fig = go.Figure()
fig.add_trace(go.Scatter(x=time_values, y=freq_roll_output, mode='markers', name='original'))
fig.add_trace(go.Scatter(x=time_values, y=filtered_freq, mode='markers', name='filtered'))
fig.show()

fig = go.Figure()
fig.add_trace(go.Scatter(x=fft_freq, y=fft_module, mode='markers', name='original'))
fig.show()
'''