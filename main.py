from get_data import get_data_from_api
from signal_processing import get_frequency_fft
from get_plots import plot_config, show_plots

start_time = 1603132200000
end_time = 1603134307000

api_data = get_data_from_api(start_time, end_time)

unix_time_values = [i[0] for i in api_data]
frequency_values = [i[1] for i in api_data]

fft_value = get_frequency_fft(frequency_values, sample_frequency=60)

# Cálculo para o espectro de potência do sinal
power_spec = fft_value['FFT'] ** 2

# Gráficos e Resultados

frequency_plot = plot_config(plot_title='Frequência da Rede',
                             x_axis_label='Tempo[unixtime]',
                             y_axis_label='Frequência[Hz]',
                             x_axis_data=unix_time_values,
                             y_axis_data=frequency_values)

fft_plot = plot_config(plot_title='Transformada de Fourier',
                       x_axis_label='Frequência[Hz]',
                       y_axis_label='Módulo',
                       x_axis_data=fft_value['Frequência'],
                       y_axis_data=fft_value['FFT'])

power_spec_plot = plot_config(plot_title='Espectro de Potência',
                              x_axis_label='Frequência[Hz]',
                              y_axis_label='Espectro de Potência',
                              x_axis_data=fft_value['Frequência'],
                              y_axis_data=power_spec)

show_plots(frequency_plot, fft_plot, power_spec_plot)
