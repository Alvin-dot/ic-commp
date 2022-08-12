import numpy as np

def get_main_peaks(welch_freq, welch_module, num_peaks=4, bandwidth=0.1, cutoff=2.5):

    flag = True
    peaks = []

    for _ in range(num_peaks):
        if (flag):
            index = welch_freq <= cutoff
        else:
            index = np.logical_or(welch_freq <= freq - bandwidth, welch_freq >= freq + bandwidth)

        welch_freq = welch_freq[index]
        welch_module = welch_module[index]

        index_max = np.argmax(welch_module)

        module = welch_module[index_max]
        freq = welch_freq[index_max]

        peaks.append([freq, module])
        flag = False
    
    return peaks