import numpy as np


def get_frequency_fft(frequency_values, sample_frequency):
    """
    Process the given frequency signal with an fast fourier transform
    Returns a dictionary containing the fft of the signal input and the x axis frequencies
    -------------
    frequency_values: list, list of the frequency values
    sample_frequency: int, sample frequency of the given signal
    """

    # Retira a componente DC do sinal de frequência
    frequency_values_mean = frequency_values - np.mean(frequency_values)

    # Número total de pontos no arquivo original
    n = len(frequency_values_mean)

    # Período de amostragem em hertz
    p = 1 / sample_frequency

    # Transformada de fourier do sinal real
    signal_fft = np.fft.rfft(frequency_values_mean, n)

    # Obtenção do módulo do número complexo
    signal_fft_module = np.abs(signal_fft)
    signal_fft_angle = np.angle(signal_fft, deg=False)

    # Obtenção das frequências pertencentes ao eixo horizontal em Hertz
    frequency_fft = np.linspace(0, np.pi / p, num=len(signal_fft), endpoint=False) / (2 * np.pi)

    return {'Frequência': frequency_fft, 'Módulo': signal_fft_module, 'Ângulo': signal_fft_angle}
