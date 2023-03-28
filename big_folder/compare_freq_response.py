import numpy as np
import pyroomacoustics as pra
import matplotlib.pyplot as plt
import scipy.signal as signal

def calculate_frequency_response(rir, fs):
    rir_norm = rir / np.max(np.abs(rir)) # normalize the RIR
    freq, response = signal.freqz(rir_norm, fs=fs) # calculate the frequency response
    return freq, response

def plot_frequency_responses(freq_responses, mic_positions):
    fig, axs = plt.subplots(len(mic_positions), 1, figsize=(8, 4 * len(mic_positions))) # create a figure with one subplot per microphone

    for i, (freq, response) in enumerate(freq_responses): # i is the mic index
        axs[i].plot(freq, 20 * np.log10(np.abs(response)))
        axs[i].set_xlabel('Frequency (Hz)')
        axs[i].set_ylabel('Amplitude (dB)')
        axs[i].set_title(f'Frequency Response at Mic Position {i}')
        axs[i].grid()

    plt.tight_layout()
    plt.show()

room_dim = [5, 4, 3]
absorption = 0.5
room = pra.ShoeBox(room_dim, fs=16000, absorption=absorption, max_order=3)

mic_positions = np.array([
    [2.5, 2, 1],
    [2.5, 2.5, 1],
    [2.5, 3, 1]
])

src_positions = np.array([
    [1, 1, 1.5],
    [3, 1, 1.5],
    [2, 1, 1.5]
])

for src_pos in src_positions:
    room.add_source(src_pos)

for mic_pos in mic_positions:
    room.add_microphone(mic_pos)

room.compute_rir()

freq_responses = []

for mic_idx in range(len(mic_positions)): # for each microphone
    MaxRIRLen = max(len(i) for i in room.rir[mic_idx]) # find the longest RIR
    combined_rir = sum(np.resize(room.rir[mic_idx][src_idx], MaxRIRLen) for src_idx in range(len(src_positions))) # combine all sources
    freq, response = calculate_frequency_response(combined_rir, room.fs) # calculate frequency response
    freq_responses.append((freq, response))

plot_frequency_responses(freq_responses, mic_positions)
