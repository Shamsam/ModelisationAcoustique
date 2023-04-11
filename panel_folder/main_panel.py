import numpy as np
import pyroomacoustics as pra
import matplotlib.pyplot as plt
import scipy.signal as signal
import panel as pn
import param
import holoviews as hv
from response_calculations import freq_resp, compute_rir, calculate_responses

pn.extension()

input_dim = pn.widgets.LiteralInput(name="Room dimensions", value=[5, 4, 3])
input_absorption = pn.widgets.FloatSlider(name="Absorption coefficient", start=0, end=1, value=0.5, step=0.1)

input_mic_pos = pn.widgets.LiteralInput(name="Mic position", value=[2.5, 2, 1])

input_src_pos = pn.widgets.LiteralInput(name="Source position", value=[1, 1, 1.5])

class Room(param.Parameterized):
    room_dim = param.List(default=[5, 5, 5])
    absorption = param.Number(default=0.5)

    @param.depends('room_dim', watch=True)
    def update_room_dim(self):
        self.room_dim = input_dim.value

    @param.depends('absorption', watch=True)
    def update_absorption(self):
        self.absorption = input_absorption.value


class Mic(param.Parameterized):
    mic_pos = param.List(default=[1, 1, 1])

    @param.depends('mic_pos', watch=True)
    def update_mic_pos(self):
        self.mic_pos = input_mic_pos.value

class Src(param.Parameterized):
    src_pos = param.List(default=[1, 1, 1])

    @param.depends('src_pos', watch=True)
    def update_src_pos(self):
        self.src_pos = input_src_pos.value

room = Room()
print(room)

""" mic_positions = {
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

freq_responses = calculate_responses(room, mic_positions, src_positions) """




