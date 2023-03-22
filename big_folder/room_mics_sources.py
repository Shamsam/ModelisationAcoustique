import numpy as np
import pyroomacoustics as pra
import matplotlib.pyplot as plt
from plot_rir_animation import plot_rir_animation
from reponse_impul_et_freq import afficherRepImpulsEtFreq

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
                    [4, 1, 1.5]
                    ])

for src_loc in src_locs:
    room.add_source(src_loc)

for mic_loc in mic_locs:
    room.add_microphone(mic_loc)

room.compute_rir() #Computes RIR between each mic and source
room.plot_rir() #Plots RIR between each mic and source
room.plot() #Plots walls, mics, source and images, no RIR, 3D
plt.show()
plot_rir_animation(room, mics=None) #pour source 0
afficherRepImpulsEtFreq(room, source=0) #pour source 0
#afficher réponse de different mic selon une source
#deux sources sur un mic
#direction des sources
#addition des rirs