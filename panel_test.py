import numpy as np
import pyroomacoustics as pra
import matplotlib.pyplot as plt
import scipy.signal as signal
import panel as pn
import holoviews as hv

pn.extension()

# Room class
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


# Helper functions
def calculate_frequency_response(rir, fs):
    rir_norm = rir / np.max(np.abs(rir))
    freq, response = signal.freqz(rir_norm, fs=fs)
    return freq, response

def plot_frequency_responses(freq_responses):
    plots = [hv.Curve((freq, 20 * np.log10(np.abs(response))), 'Frequency (Hz)', 'Amplitude (dB)').opts(title=f'Frequency Response at Mic Position {i}')
             for i, (freq, response) in enumerate(freq_responses)]
    return plots

def compute_responses(room_dim, absorption, mic_positions, src_positions):
    room = Room(room_dim, absorption)

    for src_pos in src_positions:
        room.add_source(src_pos)

    for mic_pos in mic_positions:
        room.add_microphone(mic_pos)

    room.compute_rir()

    freq_responses = []
    for mic_idx, _ in enumerate(mic_positions):
        max_rir_len = max(len(room.get_rir(mic_idx, src_idx)) for src_idx, _ in enumerate(src_positions))
        combined_rir = sum(np.resize(room.get_rir(mic_idx, src_idx), max_rir_len) for src_idx, _ in enumerate(src_positions))
        freq, response = calculate_frequency_response(combined_rir, room.get_fs())
        freq_responses.append((freq, response))

    return freq_responses

def update(event):
    mic_positions = [input_widgets[f'mic{i + 1}'].value for i in range(input_widgets['num_mics'].value)]
    src_positions = [input_widgets[f'src{i + 1}'].value for i in range(input_widgets['num_sources'].value)]

    freq_responses = compute_responses(input_widgets['room_dim'].value, input_widgets['absorption'].value, mic_positions, src_positions)
    plots = plot_frequency_responses(freq_responses)
    plot_pane.object = hv.Layout(plots).cols(1)


# input widgets dictionary
input_widgets = {
    'room_dim': pn.widgets.LiteralInput(value=(5, 4, 3), type=tuple, name='Room dimensions'),
    'absorption': pn.widgets.FloatSlider(value=0.5, start=0.0, end=1.0, step=0.01, name='Absorption'),
    'num_mics': pn.widgets.IntSlider(value=3, start=1, end=10, step=1, name='Number of Microphones'),
    'num_sources': pn.widgets.IntSlider(value=3, start=1, end=10, step=1, name='Number of Sources'),
    'mic1': pn.widgets.LiteralInput(value=(1, 1, 1), type=tuple, name='Mic Position 1'),
    'mic2': pn.widgets.LiteralInput(value=(1, 1, 1), type=tuple, name='Mic Position 2'),
    'mic3': pn.widgets.LiteralInput(value=(1, 1, 1), type=tuple, name='Mic Position 3'),
    'src1': pn.widgets.LiteralInput(value=(1, 1, 1), type=tuple, name='Source Position 1'),
    'src2': pn.widgets.LiteralInput(value=(1, 1, 1), type=tuple, name='Source Position 2'),
    'src3': pn.widgets.LiteralInput(value=(1, 1, 1), type=tuple, name='Source Position 3')
}


def update_positions(event):
    num_positions = event.new
    prefix = 'Mic' if event.obj is input_widgets['num_mics'] else 'Source'

    for i in range(num_positions, 10):  # Remove unused position widgets from input_widgets dictionary
        if f'{prefix.lower()}{i + 1}' in input_widgets:
            del input_widgets[f'{prefix.lower()}{i + 1}']

    position_inputs = update_positions(num_positions, prefix)

    for i, widget in enumerate(position_inputs):  # Add the new position widgets to the input_widgets dictionary
        input_widgets[f'{prefix.lower()}{i + 1}'] = widget

    update_inputs_layout()

def update_inputs_layout():
    inputs_layout = [input_widgets['room_dim'], input_widgets['absorption'], input_widgets['num_mics'], input_widgets['num_sources']]

    mic_positions = [input_widgets[f'mic{i + 1}'] for i in range(input_widgets['num_mics'].value)]
    src_positions = [input_widgets[f'src{i + 1}'] for i in range(input_widgets['num_sources'].value)]

    inputs_layout.append(pn.Column(*mic_positions))
    inputs_layout.append(pn.Column(*src_positions))

    inputs[:] = inputs_layout  # Update the inputs panel with the new layout

# Update the position input widgets when the number of microphones or sources changes
input_widgets['num_mics'].param.watch(update_positions, 'value')
input_widgets['num_sources'].param.watch(update_positions, 'value')

inputs = pn.Column()  # Create an empty inputs panel
update_inputs_layout()  # Initialize the inputs panel with the correct layout

# Initialize the plot pane with the initial frequency responses
initial_freq_responses = compute_responses(
    input_widgets['room_dim'].value, input_widgets['absorption'].value,
    [input_widgets['mic1'].value, input_widgets['mic2'].value, input_widgets['mic3'].value],
    [input_widgets['src1'].value, input_widgets['src2'].value, input_widgets['src3'].value]
)

initial_plots = plot_frequency_responses(initial_freq_responses)
plot_pane = pn.pane.HoloViews(hv.Layout(initial_plots).cols(1), width=800, height=400)

# Create the app layout with the inputs panel and the plot pane
app = pn.Row(inputs, plot_pane)
app.servable()
