import numpy as np


def get_frequency_fft(frequency_values, sample_frequency):

    # Retira a componente DC do sinal de frequência
    frequency_values_mean = frequency_values - np.mean(frequency_values)

    # Número total de pontos no arquivo original
    n = len(frequency_values_mean)

    # Período de amostragem em hertz
    p = 1 / sample_frequency

    # Transformada de fourier do sinal real
    signal_fft = np.fft.rfft(frequency_values_mean, n)

    # Obtenção do módulo e ângulo do número complexo
    signal_fft_module = np.abs(signal_fft)
    # signal_fft_angle = np.angle(signal_fft, deg=True)

    # Obtenção das frequências pertencentes ao eixo horizontal em Hertz
    frequency_fft = np.linspace(0, np.pi / p, num=len(signal_fft), endpoint=False) / (2 * np.pi)

    return {'Frequência': frequency_fft, 'FFT': signal_fft_module}
