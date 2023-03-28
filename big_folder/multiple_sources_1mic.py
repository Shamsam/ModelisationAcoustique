import numpy as np
import pyroomacoustics as pra
import matplotlib.pyplot as plt
import scipy.signal as signal

def adding_rir(room, mic, sources):
    
    MaxRIRLen = max(len(i) for i in room.rir[mic])
    rirtot = sum(np.resize(room.rir[mic][i], MaxRIRLen) for i in sources)
    rirtot = rirtot / np.max(np.abs(rirtot))
    freq, response = signal.freqz(rirtot, fs=room.fs)

    fig, axs = plt.subplots(len(sources) + 1, 1, figsize=(8, 6 * (len(sources) + 1)))

    for i, src in enumerate(sources):
        axs[i].plot(room.rir[mic][src])
        axs[i].set_xlabel('Time (samples)')
        axs[i].set_ylabel('Amplitude')
        axs[i].set_title(f'Room Impulse Response for Source {src}')
    
    axs[-1].plot(rirtot)
    axs[-1].set_xlabel('Time (samples)')
    axs[-1].set_ylabel('Amplitude')
    axs[-1].set_title('Combined Room Impulse Response')

    plt.tight_layout()
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
