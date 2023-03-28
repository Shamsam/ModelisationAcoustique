import numpy as np
import pyroomacoustics as pra
import matplotlib.pyplot as plt
import scipy.signal as signal

def adding_rir(room, mic, sources):
    
    MaxRIRLen = max(len(i) for i in room.rir[mic])
    rirtot = sum(np.resize(room.rir[mic][i], MaxRIRLen) for i in sources)
    rirtot = rirtot / np.max(np.abs(rirtot))
    freq, response = signal.freqz(rirtot, fs=room.fs)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    colors = ['r', 'g', 'b', 'm', 'c', 'y', 'k']

    for i, src in enumerate(sources):
        color = colors[i % len(colors)]
        ax1.plot(room.rir[mic][src], color=color, label=f'Source {src}')
    
    ax1.set_xlabel('Time (samples)')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Individual Room Impulse Responses')
    ax1.legend()

    ax2.plot(rirtot)
    ax2.set_xlabel('Time (samples)')
    ax2.set_ylabel('Amplitude')
    ax2.set_title('Combined Room Impulse Response')

    plt.show()

    fig2, ax = plt.subplots(figsize=(8, 6))
    ax.plot(np.abs(freq), 20 * np.log10(np.abs(response)))
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Amplitude (dB)')
    ax.set_title('Frequency Response of the Combined Room Impulse Response') #specific to the position of the microphone
    ax.grid()

    plt.show()


room_dim = [5, 4, 3]
absorption = 0.5

room = pra.ShoeBox(room_dim, fs=16000, absorption=absorption, max_order=3)

mic_locs = np.array([
                    [2.5, 2, 1], 
                    [2.5, 2.5, 1], 
                    [2.5, 3, 1]
                    ])

src_locs = np.array([
                    [1, 1, 1.5], 
                    [3, 1, 1.5],
                    [2, 1, 1.5] 
                    ])

for src_loc in src_locs:
    room.add_source(src_loc)

for mic_loc in mic_locs:
    room.add_microphone(mic_loc)

room.compute_rir() 
adding_rir(room, mic=0, sources=[0, 1, 2])
