import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

def afficherRepImpulsEtFreq(room, source):
    # Obtenir la réponse impulsionnelle et la normaliser
    rir = room.rir[0][source]
    rir = rir / np.max(np.abs(rir))

    # Obtenir la réponse fréquentielle
    freq, response = signal.freqz(rir, fs=room.fs)

    # Créer une figure avec deux sous-figures
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

    # Afficher la réponse impulsionnelle
    ax1.plot(rir)
    ax1.set_xlabel('Temps (échantillons)')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Réponse impulsionnelle de la pièce')

    # Afficher la réponse fréquentielle
    ax2.plot(np.abs(freq), 20 * np.log10(np.abs(response)))
    ax2.set_xlabel('Fréquence (Hz)')
    ax2.set_ylabel('Amplitude (dB)')
    ax2.set_title('Réponse fréquentielle de la pièce') #corriger mic 0 or 1 or 2
    ax2.grid()

    # Afficher la figure
    plt.tight_layout()
    plt.show()