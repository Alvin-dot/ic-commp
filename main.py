from get_data import get_data_from_api
from datetime import datetime
from scipy import signal
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import time

# Sampling rate given in Hz
data_freq = 5
# Set the data time window in hours
data_time_window = 1
# Set the refresh time window in minutes
refresh_time_window = 5

reset_flag = True

# Get the hour time window from current time in unix milisseconds format
end_time_str = datetime.now()
end_time_unix = int(end_time_str.timestamp() * 1000)
start_time_unix = end_time_unix - (data_time_window * 3600 * 1000)

# Get the frequency data based on the start and end time
api_data = get_data_from_api(start_time_unix, end_time_unix, interval=data_freq, interval_type=1, skip_missing=0)

unix_time_values = [i[0] for i in api_data]
frequency_values = [i[1] for i in api_data]

while True:

    if not reset_flag:
        # Gets 5 minutes window for data refreshing
        start_time_unix = end_time_unix
        end_time_unix += refresh_time_window * 60 * 1000

        # Get the frequency data based on the start and end time
        api_data = get_data_from_api(start_time_unix, end_time_unix, interval=data_freq, interval_type=1,
                                     skip_missing=0)

        # Replaces data into lists
        del unix_time_values[:(refresh_time_window * 60 * data_freq) - 1]
        del frequency_values[:(refresh_time_window * 60 * data_freq) - 1]

        for i in api_data:
            unix_time_values.append(i[0])
            frequency_values.append(i[1])

    # Converts unix time to Numpy DateTime64 time milisseconds and converts from GMT time to local time
    time_values = [np.datetime64(int(i - (3 * 3600000)), 'ms') for i in unix_time_values]

    # Creates dataframe for variables
    df = pd.DataFrame({"freq": frequency_values, "date": time_values, "original_freq": frequency_values})

    # -----------------------------------
    # Treatment of missing data
    # -----------------------------------

    # Replaces None values with NaN
    df["freq"].fillna(np.NaN, inplace=True)

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

    # Uses Welch method for FFT calculation
    fft_freq, fft_module = signal.welch(db, fs=data_freq, nperseg=(len(df["freq"])) // 20,
                                        average='mean', detrend='constant')

    # -----------------------------------
    # Plotting
    # -----------------------------------

    # Writes plot values in a csv file
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_values, y=df["original_freq"], mode='lines'))
    fig.update_layout(title="Gráfico da frequência da rede no tempo", xaxis_title="Tempo", yaxis_title="Frequência [Hz]")
    fig.write_image("/opt/ic-commp/Grafico1.png")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fft_freq, y=fft_module, mode='lines+markers'))
    fig.update_layout(title="Transformada de Welch", xaxis_title="Frequência [Hz]", yaxis_title="Módulo")
    fig.write_image("/opt/ic-commp/Grafico2.png")

    reset_flag = False

    # Awaits for determined refresh time
    time.sleep(refresh_time_window * 60)
