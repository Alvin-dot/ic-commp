from get_data import get_data_from_api
from signal_processing import get_frequency_fft
from datetime import datetime
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from scipy import signal, stats

# Get start and end time in unix time milisseconds
start_time_str = datetime.strptime('14.11.2020 05:00:00', '%d.%m.%Y %H:%M:%S')
start_time_unix = start_time_str.timestamp() * 1000

end_time_str = datetime.strptime('14.11.2020 06:00:00', '%d.%m.%Y %H:%M:%S')
end_time_unix = end_time_str.timestamp() * 1000

# Frequency value derived from 4.1.5 downsampling
data_freq = 5

# Get the frequency data based on the start and end time
api_data = get_data_from_api(start_time_unix, end_time_unix, interval=data_freq, interval_type=1, skip_missing=0)

unix_time_values = [i[0] for i in api_data]
frequency_values = [i[1] for i in api_data]

# Converts unix time from GMT time to local time and removes milisseconds
time_values = [(i - (3 * 3600000)) for i in unix_time_values]
# Converts unix time to Numpy DateTime64 time
time_values = [np.datetime64(int(i), 'ms') for i in time_values]

# Creates dataframe for variables
df = pd.DataFrame({"freq": frequency_values, "date": time_values, "original_freq": frequency_values})

# -----------------------------------
# Treatment of missing data
# -----------------------------------

# Replaces None values with NaN
df["freq"].fillna(np.NaN)

# -----------------------------------
# Treatment of outliers
# -----------------------------------

# ROLLING MEAN AND STANDARD DEVIATION METHOD
roll_window = 20
alpha = 3

# Calculate moving average
df["roll_mean"] = df.freq.rolling(window=roll_window).mean()

# Pad first 20 values with same as the original data
df.loc[:roll_window - 1, "roll_mean"] = df.loc[:roll_window - 1, "freq"]

for i in range(len(df["roll_mean"])):
    if not ((abs(df["roll_mean"][i]) + alpha * df["freq"].std()) > abs(df["freq"][i]) >
            (abs(df["roll_mean"][i]) - alpha * df["freq"].std())):
        df.loc[i, "freq"] = np.NaN

# -----------------------------------
# Interpolation process
# -----------------------------------

# Replaces NaN values with mean value
for i in range(len(df["freq"])):
    if df["freq"][i] != df["freq"][i]:
        df.loc[i, "freq"] = df["freq"].mean()

# -----------------------------------
# Removal of signal average
# -----------------------------------
df.loc[:, "freq"] -= df["freq"].mean()

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

# fft_module, fft_freq, fft_angle = get_frequency_fft(db, data_freq)

fft_freq, fft_module = signal.welch(db, fs=data_freq, nperseg=(len(df["freq_filter"]))//20,
                                    average='mean', detrend='constant')

# -----------------------------------
# Plotting
# -----------------------------------
fig = go.Figure()
fig.add_trace(go.Scatter(x=time_values, y=df["freq"], mode='lines', name='sinal original'))
fig.add_trace(go.Scatter(x=time_values, y=df["freq_filter"], mode='lines', name='sinal filtrado'))
fig.update_layout(title="Gráfico da frequência da rede no tempo", xaxis_title="Tempo", yaxis_title="Frequência [Hz]")
fig.show()

fig = go.Figure()
fig.add_trace(go.Scatter(x=fft_freq, y=fft_module, mode='markers'))
fig.update_layout(title="Transformada de Welch", xaxis_title="Frequência [Hz]", yaxis_title="Módulo")
fig.show()
