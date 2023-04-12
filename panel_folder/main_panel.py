import numpy as np
import pyroomacoustics as pra
import matplotlib.pyplot as plt
import scipy.signal as signal
import panel as pn
import holoviews as hv

pn.extension()

class Room:
    def __init__(self, room_dim, absorption, fs=16000, max_order=3):
        self.room = pra.ShoeBox(room_dim, fs=fs, absorption=absorption, max_order=max_order)

    def add_microphone(self, mic_position):
        self.room.add_microphone(mic_position)

    def add_source(self, src_position):
        self.room.add_source(src_position)

    def compute_rir(self):
        self.room.compute_rir()

    def get_rir(self, mic_idx, src_idx):
        return self.room.rir[mic_idx][src_idx]

    def get_fs(self):
        return self.room.fs

class Microphone:
    def __init__(self, position):
        self.position = position

class Source:
    def __init__(self, position):
        self.position = position


def calculate_frequency_response(rir, fs):
    rir_norm = rir / np.max(np.abs(rir)) # normalize the RIR
    freq, response = signal.freqz(rir_norm, fs=fs) # calculate the frequency response
    return freq, response

def plot_frequency_responses(freq_responses):
    plots = []
    for i, (freq, response) in enumerate(freq_responses): # i is the mic index
        curve = hv.Curve((freq, 20 * np.log10(np.abs(response))), 'Frequency (Hz)', 'Amplitude (dB)').opts(title=f'Frequency Response at Mic Position {i}')
        plots.append(curve)
    return plots

def compute_responses(room_dim, absorption, mic_positions, src_positions):
    room = pra.ShoeBox(room_dim, fs=16000, absorption=absorption, max_order=3)

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

    return freq_responses

def update(event):
    room_dim = room_dim_input.value
    absorption = absorption_input.value
    mic_positions = np.array([mic1_input.value, mic2_input.value, mic3_input.value])
    src_positions = np.array([src1_input.value, src2_input.value, src3_input.value])

    room = Room(room_dim, absorption)
    microphones = [Microphone(pos) for pos in mic_positions]
    sources = [Source(pos) for pos in src_positions]

    for mic in microphones:
        room.add_microphone(mic.position)

    for src in sources:
        room.add_source(src.position)

    room.compute_rir()

    freq_responses = []

    for mic_idx in range(len(microphones)): # for each microphone
        MaxRIRLen = max(len(room.get_rir(mic_idx, src_idx)) for src_idx in range(len(sources))) # find the longest RIR
        combined_rir = sum(np.resize(room.get_rir(mic_idx, src_idx), MaxRIRLen) for src_idx in range(len(sources))) # combine all sources
        freq, response = calculate_frequency_response(combined_rir, room.get_fs()) # calculate frequency response
        freq_responses.append((freq, response))

    plots = plot_frequency_responses(freq_responses)
    plot_pane.object = hv.Layout(plots).cols(1)

room_dim_input = pn.widgets.LiteralInput(value=(5, 4, 3), type=tuple, name='Room dimensions')
absorption_input = pn.widgets.FloatSlider(value=0.5, start=0.0, end=1.0, step=0.01, name='Absorption')

mic1_input = pn.widgets.LiteralInput(value=(2.5, 2, 1), type=tuple, name='Mic Position 1')
mic2_input = pn.widgets.LiteralInput(value=(2.5, 2.5, 1), type=tuple, name='Mic Position 2')
mic3_input = pn.widgets.LiteralInput(value=(2.5, 3, 1), type=tuple, name='Mic Position 3')

src1_input = pn.widgets.LiteralInput(value=(1, 1, 1.5), type=tuple, name='Source Position 1')
src2_input = pn.widgets.LiteralInput(value=(3, 1, 1.5), type=tuple, name='Source Position 2')
src3_input = pn.widgets.LiteralInput(value=(2, 1, 1.5), type=tuple, name='Source Position 3')

room_dim_input.param.watch(update, 'value')
absorption_input.param.watch(update, 'value')

mic1_input.param.watch(update, 'value')
mic2_input.param.watch(update, 'value')
mic3_input.param.watch(update, 'value')

src1_input.param.watch(update, 'value')
src2_input.param.watch(update, 'value')
src3_input.param.watch(update, 'value')

initial_freq_responses = compute_responses(room_dim_input.value, absorption_input.value, np.array([mic1_input.value, mic2_input.value, mic3_input.value]), np.array([src1_input.value, src2_input.value, src3_input.value]))
initial_plots = plot_frequency_responses(initial_freq_responses)
plot_pane = pn.pane.HoloViews(hv.Layout(initial_plots).cols(1), width=800, height=400)

inputs = pn.Column(room_dim_input, absorption_input, mic1_input, mic2_input, mic3_input, src1_input, src2_input, src3_input)

app = pn.Row(inputs, plot_pane)
app.servable()

# panel serve --show --autoreload panel_folder/main_panel.py