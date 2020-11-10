import numpy as np


def get_frequency_fft(frequency_values, sample_frequency):
    """
    Process the given frequency signal with an fast fourier transform
    Returns a dictionary containing the fft of the signal input and the x axis frequencies
    -------------
    frequency_values: list, list of the frequency values
    sample_frequency: int, sample frequency of the given signal
    """

    # Número total de pontos no arquivo original
    n = len(frequency_values)

    # Transformada de fourier do sinal real
    signal_fft = np.fft.rfft(frequency_values, n)

    # Obtenção do módulo do número complexo
    signal_fft_module = np.abs(signal_fft)
    signal_fft_angle = np.angle(signal_fft, deg=False)

    # Obtenção das frequências pertencentes ao eixo horizontal em Hertz
    frequency_fft = np.linspace(0, np.pi * sample_frequency, num=len(signal_fft), endpoint=True) / (2 * np.pi)

    return signal_fft_module, frequency_fft, signal_fft_angle
