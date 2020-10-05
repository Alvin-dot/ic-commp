import csv
import matplotlib.pyplot as plt
import numpy as np

# Abre o arquivo CSV como uma lista de dicionários
with open('515_new.csv') as csv_file:
    origin_file = list(csv.DictReader(csv_file))

frequency_values = []
date_values = []

# Separa os valores de tempo e frequência em suas próprias listas
for i in origin_file:
    date_values.append(i['Date'])
    frequency_values.append(i['Value'])

frequency_values_float = []

# Transforma os valores de frequência de 'string' para 'float'
for i in frequency_values:
    if i != "":
        frequency_values_float.append(float(i))

# Processamento dos dados

# Número total de pontos no arquivo
n = len(frequency_values_float)

# Período de amostragem
p = 1/120

# Transformada de fourier do sinal
signal_fft = np.fft.fft(frequency_values_float, n)

# Obtenção do módulo e ângulo do número complexo
signal_fft_module = np.abs(signal_fft)
signal_fft_angle = np.angle(signal_fft, deg=True)

# Obtenção das frequências pertencentes ao eixo horizontal
frequency_fft = np.linspace(0, 2*np.pi/p, num=n, endpoint=False)

# Filtro para valores muito altos do módulo da FFT
filt = signal_fft_module < 5000

# Cálculo para o espectro de frequência do sinal
power_spec = signal_fft_module ** 2

# Gráfico do sinal de frequência original
fig_original, ax0 = plt.subplots(figsize=(14, 6))
ax0.plot(range(len(frequency_values_float)), frequency_values_float)
ax0.set_title('Sinal de frequência original')
ax0.set_xlabel('Número de amostras')
ax0.set_ylabel('Frequência [Hz]')
ax0.grid(alpha=0.3)

plt.show()

# Gráfico do módulo e ângulo da FFT sem filtro
fig_no_filter, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 6))
fig_no_filter.suptitle('FFT do sinal de frequência sem filtro')
ax1.plot(frequency_fft, signal_fft_module)
ax1.set_ylabel('Módulo')
ax1.grid(alpha=0.3)
ax2.plot(frequency_fft, signal_fft_angle)
ax2.set_ylabel('Ângulo [°]')
ax2.set_xlabel('Frequência [rad/s]')
ax2.grid(alpha=0.3)

plt.show()

# Gráfico do módulo e ângulo da FFT com filtro filtro
fig_filter, (ax3, ax4) = plt.subplots(2, 1, figsize=(14, 6))
fig_filter.suptitle('FFT do sinal de frequência filtrado')
ax3.plot(frequency_fft[filt], signal_fft_module[filt])
ax3.set_ylabel('Módulo')
ax3.grid(alpha=0.3)
ax4.plot(frequency_fft[filt], signal_fft_angle[filt])
ax4.set_ylabel('Ângulo [°]')
ax4.set_xlabel('Frequência [rad/s]')
ax4.grid(alpha=0.3)

plt.show()

# Gráfico do espectro de potência do sinal
fig_power, ax5 = plt.subplots(figsize=(14, 6))
ax5.plot(frequency_fft[filt], power_spec[filt])
ax5.set_title('Espectro de potência do sinal de frequência filtrado')
ax5.set_xlabel('Frequência [rad/s]')
ax5.set_ylabel('Espectro de potência')
ax5.grid(alpha=0.3)

plt.show()


'''
Frequência de amostragem de 120 Hz
Fazer o plot em um espaço linear entre 0 e 2pi/período de amostragem (approx 754 rad/s)
O primeiro valor da fft corresponde a 0 rad e o último valor corresponde a um intervalo a menos de 2pi/período de 
amostragem
Fazer o plot do módulo e do ângulo do sinal da FFT recebido
Espectro de potência é o módulo da FFT ao quadrado

Cada intervalo de frequência
O ultimo ponto é 2pi/período de amostragem -> Ultimo valor do fft (eixo da escala x)

ESTA É UMA ALTERAÇÃO PRA TESTAR O GIT
ESTA É OUTRA ALTERAÇÃO PRA TESTAR O GIT HEHEHEH
Esta é uma alteração ainda maior
'''
