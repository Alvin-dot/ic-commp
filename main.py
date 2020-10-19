import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.models import HoverTool
from bokeh.models.tickers import AdaptiveTicker
from bokeh.layouts import column

# Importa o arquivo CSV como um array
origin_file = pd.read_csv('515.csv', na_filter=False)

# Separa os valores de tempo e frequência em suas próprias listas
date_values = np.array([d for d in origin_file['Date']])
frequency_values = np.array([f for f in origin_file['Value'] if f != ""])

# Retira a componente DC do sinal de frequência
frequency_values_mean = frequency_values - np.mean(frequency_values)

# Processamento dos dados

# Número total de pontos no arquivo original
n = len(frequency_values_mean)

# Período de amostragem em hertz
fr = 1
p = 1 / fr

# Transformada de fourier do sinal real
signal_fft = np.fft.rfft(frequency_values_mean, n)

# Obtenção do módulo e ângulo do número complexo
signal_fft_module = np.abs(signal_fft)
signal_fft_angle = np.angle(signal_fft, deg=True)

# Obtenção das frequências pertencentes ao eixo horizontal em Hertz
frequency_fft = np.linspace(0, np.pi / p, num=len(signal_fft), endpoint=False) / (2 * np.pi)

# Cálculo para o espectro de potência do sinal
power_spec = signal_fft_module ** 2

# Gráficos e Resultados

# Configura exportação dos resultados
output_file('results.html')

# Gráfico sinal original
original_signal_df = pd.DataFrame({'Frequência[Hz]': frequency_values,
                                   'Número de amostras': range(len(frequency_values))})

tt_01 = HoverTool(tooltips=[
    ("Frequência[Hz]", "@{Frequência[Hz]}"),
    ("Número da amostra", "@{Número de amostras}")
])

original_signal_plot = figure(title="Sinal de Frequência Original",
                              x_axis_label='Número de amostras',
                              y_axis_label='Frequência[Hz]',
                              plot_width=1200,
                              plot_height=600,
                              tools=[tt_01, 'wheel_zoom', 'pan', 'reset'])
original_signal_plot.line('Número de amostras', 'Frequência[Hz]', line_width=2, source=original_signal_df, alpha=0.8)
original_signal_plot.yaxis.ticker = AdaptiveTicker(desired_num_ticks=10)
original_signal_plot.title.text_font_size = '16pt'
original_signal_plot.axis.axis_label_text_font_style = 'bold'

# Gráfico fft
module_fft_df = pd.DataFrame({'Módulo': signal_fft_module,
                              'Frequência[Hz]': frequency_fft})

tt_02 = HoverTool(tooltips=[
    ("Módulo", "@{Módulo}"),
    ("Frequência[Hz]", "@{Frequência[Hz]}")
])

fft_module_plot = figure(title="Transformada de Fourier",
                         x_axis_label='Frequência[Hz]',
                         y_axis_label='Módulo',
                         plot_width=1200,
                         plot_height=600,
                         tools=[tt_02, 'wheel_zoom', 'pan', 'reset'])
fft_module_plot.line('Frequência[Hz]', 'Módulo', line_width=2, source=module_fft_df, alpha=0.8)
fft_module_plot.title.text_font_size = '16pt'
fft_module_plot.axis.axis_label_text_font_style = 'bold'

# Gráfico espectro de potência
ps_sinal_df = pd.DataFrame({'Espectro de Potência': power_spec,
                            'Frequência[Hz]': frequency_fft})

tt_03 = HoverTool(tooltips=[
    ("Espectro de Potência", "@{Espectro de Potência}"),
    ("Frequência[Hz]", "@{Frequência[Hz]}")
])

ps_signal_plot = figure(title="Espectro de Potência",
                        x_axis_label='Frequência[Hz]',
                        y_axis_label='Espectro de Potência',
                        plot_width=1200,
                        plot_height=600,
                        tools=[tt_03, 'wheel_zoom', 'pan', 'reset'])
ps_signal_plot.line('Frequência[Hz]', 'Espectro de Potência', line_width=2, source=ps_sinal_df, alpha=0.8)
ps_signal_plot.title.text_font_size = '16pt'
ps_signal_plot.axis.axis_label_text_font_style = 'bold'

show(column(original_signal_plot, fft_module_plot, ps_signal_plot))
