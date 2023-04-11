import numpy as np
import pyroomacoustics as pra
import matplotlib.pyplot as plt
import scipy.signal as signal
import panel as pn
import holoviews as hv
from response_calculations import freq_resp, compute_rir, calculate_responses

pn.extension()

input_dim = pn.widgets.ArrayInput(name="Room dimensions", value=[5, 4, 3], type=np.float64)
input_absorption = pn.widgets.FloatSlider(name="Absorption coefficient", start=0, end=1, value=0.5, step=0.1)

room_dim = [5, 4, 3]
absorption = 0.5
room = pra.ShoeBox(room_dim, fs=16000, absorption=absorption, max_order=3)


mic_positions = {
    "mic_1": [2.5, 2, 1],
    "mic_2": [2.5, 2.5, 1],
    "mic_3": [2.5, 3, 1]
}

src_positions = {
    "src_1": [1, 1, 1.5],
    "src_2": [3, 1, 1.5],
    "src_3": [2, 1, 1.5]
}

room = compute_rir(room_dim, absorption, 3, mic_positions, src_positions)

freq_responses = calculate_responses(room, mic_positions, src_positions)




