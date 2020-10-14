import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.models import HoverTool
from bokeh.models.tickers import AdaptiveTicker
from bokeh.layouts import column

# Importa o arquivo CSV como um array
origin_file = pd.read_csv('515_new.csv', na_filter=False)

# Separa os valores de tempo e frequência em suas próprias listas
date_values = np.array([d for d in origin_file['Date']])
frequency_values = np.array([f for f in origin_file['Value'] if f != ""])

# Processamento dos dados

# Número total de pontos no arquivo original
n = len(frequency_values)

# Período de amostragem
p = 1 / 120

# Transformada de fourier do sinal real
signal_fft = np.fft.rfft(frequency_values, n)

# Obtenção do módulo e ângulo do número complexo
signal_fft_module = np.abs(signal_fft)
signal_fft_angle = np.angle(signal_fft, deg=True)

# Obtenção das frequências pertencentes ao eixo horizontal
frequency_fft = np.linspace(0, 2 * np.pi / p, num=len(signal_fft), endpoint=False)

# Filtro para valores muito altos do módulo da FFT
filt = signal_fft_module < 5000

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
                              tools=[tt_01])
original_signal_plot.line('Número de amostras', 'Frequência[Hz]', line_width=2, source=original_signal_df, alpha=0.8)
original_signal_plot.yaxis.ticker = AdaptiveTicker(desired_num_ticks=10)
original_signal_plot.title.text_font_size = '16pt'
original_signal_plot.axis.axis_label_text_font_style = 'bold'

# Gráfico fft sem filtro
no_filter_module_fft = pd.DataFrame({'Módulo': signal_fft_module,
                                     'Frequência[rad/s]': frequency_fft})

tt_02 = HoverTool(tooltips=[
    ("Módulo", "@{Módulo}"),
    ("Frequência[rad/s]", "@{Frequência[rad/s]}")
])

no_filter_module_plot = figure(title="Transformada de Fourier - Sem filtro",
                               y_axis_label='Módulo',
                               plot_width=1200,
                               plot_height=400,
                               tools=[tt_02])
no_filter_module_plot.line('Frequência[rad/s]', 'Módulo', line_width=2, source=no_filter_module_fft, alpha=0.8)
no_filter_module_plot.title.text_font_size = '16pt'
no_filter_module_plot.axis.axis_label_text_font_style = 'bold'

no_filter_angle_fft = pd.DataFrame({'Ângulo[°]': signal_fft_angle,
                                    'Frequência[rad/s]': frequency_fft})

tt_03 = HoverTool(tooltips=[
    ("Ângulo[°]", "@{Ângulo[°]}"),
    ("Frequência[rad/s]", "@{Frequência[rad/s]}")
])

no_filter_angle_plot = figure(title="",
                              x_axis_label='Frequência[rad/s]',
                              y_axis_label='Ângulo[°]',
                              plot_width=1200,
                              plot_height=400,
                              tools=[tt_03])
no_filter_angle_plot.line('Frequência[rad/s]', 'Ângulo[°]', line_width=2, source=no_filter_angle_fft, alpha=0.8,
                          line_color='orange')
no_filter_angle_plot.axis.axis_label_text_font_style = 'bold'

# Gráfico fft filtrado
filtered_module_fft = pd.DataFrame({'Módulo': signal_fft_module[filt],
                                    'Frequência[rad/s]': frequency_fft[filt]})

filtered_module_plot = figure(title="Transformada de Fourier - Filtrado",
                              y_axis_label='Módulo',
                              plot_width=1200,
                              plot_height=420,
                              tools=[tt_02])
filtered_module_plot.line('Frequência[rad/s]', 'Módulo', line_width=2, source=filtered_module_fft, alpha=0.8)
filtered_module_plot.title.text_font_size = '16pt'
filtered_module_plot.axis.axis_label_text_font_style = 'bold'

filtered_angle_fft = pd.DataFrame({'Ângulo[°]': signal_fft_angle[filt],
                                   'Frequência[rad/s]': frequency_fft[filt]})

filtered_angle_plot = figure(x_axis_label='Frequência[rad/s]',
                             y_axis_label='Ângulo[°]',
                             plot_width=1200,
                             plot_height=400,
                             tools=[tt_03])
filtered_angle_plot.line('Frequência[rad/s]', 'Ângulo[°]', line_width=2, source=filtered_angle_fft, alpha=0.8,
                         line_color='orange')
filtered_angle_plot.axis.axis_label_text_font_style = 'bold'

# Gráfico espectro de potência
ps_sinal_df = pd.DataFrame({'Espectro de Potência': power_spec[filt],
                             'Frequência[rad/s]': frequency_fft[filt]})

tt_04 = HoverTool(tooltips=[
    ("Espectro de Potência", "@{Espectro de Potência}"),
    ("Frequência[rad/s]", "@{Frequência[rad/s]}")
])

ps_signal_plot = figure(title="Espectro de Potência",
                        x_axis_label='Frequência[rad/s]',
                        y_axis_label='Espectro de Potência',
                        plot_width=1200,
                        plot_height=600,
                        tools=[tt_04])
ps_signal_plot.line('Frequência[rad/s]', 'Espectro de Potência', line_width=2, source=ps_sinal_df, alpha=0.8)
ps_signal_plot.title.text_font_size = '16pt'
ps_signal_plot.axis.axis_label_text_font_style = 'bold'

show(column(original_signal_plot,
            no_filter_module_plot, no_filter_angle_plot,
            filtered_module_plot, filtered_angle_plot,
            ps_signal_plot))

'''
Frequência de amostragem de 120 Hz
Fazer o plot em um espaço linear entre 0 e 2pi/período de amostragem (approx 754 rad/s)
O primeiro valor da fft corresponde a 0 rad e o último valor corresponde a um intervalo a menos de 2pi/período de 
amostragem
Fazer o plot do módulo e do ângulo do sinal da FFT recebido
Espectro de potência é o módulo da FFT ao quadrado

Cada intervalo de frequência
O ultimo ponto é 2pi/período de amostragem -> Ultimo valor do fft (eixo da escala x)
'''
