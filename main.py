from get_data import get_data_from_api
from signal_processing import get_frequency_fft
from get_plots import plot_config, show_plots
from datetime import datetime

# Get start and end time
start_time_str = datetime.strptime('02.11.2020 10:00:00', '%d.%m.%Y %H:%M:%S')
start_time_unix = start_time_str.timestamp() * 1000

end_time_str = datetime.strptime('02.11.2020 12:00:00', '%d.%m.%Y %H:%M:%S')
end_time_unix = end_time_str.timestamp() * 1000

data_freq = 120

# Get the frequency data based on the start and end time
api_data = get_data_from_api(start_time_unix, end_time_unix, interval=data_freq, interval_type=1)

# Converts unix time from GMT time to local time
unix_time_values = [i[0] - (3 * 3600000) for i in api_data]
frequency_values = [i[1] for i in api_data]

# Process the fft of the signal
fft_value = get_frequency_fft(frequency_values, sample_frequency=data_freq)

# Calculates the power spec of the fft
power_spec = fft_value['Módulo'] ** 2

# Original frequency signal plot
frequency_plot = plot_config(plot_title=f'Frequência da Rede @{data_freq} Hz',
                             x_axis_label='Tempo',
                             y_axis_label='Frequência[Hz]',
                             x_axis_data=unix_time_values,
                             y_axis_data=frequency_values,
                             x_axis_type='datetime')

# Fast fourier transform plot
fft_plot = plot_config(plot_title=f'Transformada de Fourier @{data_freq} Hz',
                       x_axis_label='Frequência[Hz]',
                       y_axis_label='Módulo',
                       x_axis_data=fft_value['Frequência'],
                       y_axis_data=fft_value['Módulo'],
                       x_min=-0.05,
                       x_max=10)

# Power spec plot
power_spec_plot = plot_config(plot_title=f'Espectro de Potência @{data_freq} Hz',
                              x_axis_label='Frequência[Hz]',
                              y_axis_label='Espectro de Potência',
                              x_axis_data=fft_value['Frequência'],
                              y_axis_data=power_spec,
                              x_min=-0.05,
                              x_max=10)

# Show all plot on a column
show_plots(frequency_plot, fft_plot, power_spec_plot)
