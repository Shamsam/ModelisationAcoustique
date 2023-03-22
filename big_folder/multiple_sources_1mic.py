import numpy as np
import pyroomacoustics as pra
import matplotlib.pyplot as plt
import scipy.signal as signal

def adding_rir(room, mic, sources):

    rirtot = 0

    for i in range(sources):
        rirtot += room.rir[mic][i]

    rirtot = rirtot / np.max(np.abs(rirtot))
    freq, response = signal.freqz(rirtot, fs=room.fs)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

    ax1.plot(rirtot)
    ax1.set_xlabel('Temps (échantillons)')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Réponse impulsionnelle de la pièce')

    ax2.plot(np.abs(freq), 20 * np.log10(np.abs(response)))
    ax2.set_xlabel('Fréquence (Hz)')
    ax2.set_ylabel('Amplitude (dB)')
    ax2.set_title('Réponse fréquentielle de la pièce')
    ax2.grid()

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
                    [2, 1, 1.5] #error broadcasting shapes
                    ])

for src_loc in src_locs:
    room.add_source(src_loc)

for mic_loc in mic_locs:
    room.add_microphone(mic_loc)

room.compute_rir() 
adding_rir(room, mic=0, sources=room.n_sources)