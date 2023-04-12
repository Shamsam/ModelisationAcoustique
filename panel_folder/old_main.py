import numpy as np
import pyroomacoustics as pra
import matplotlib.pyplot as plt
import scipy.signal as signal
import panel as pn
import param
import holoviews as hv
from response_calculations import freq_resp, compute_rir, calculate_responses, plot_freq_response

pn.extension()

room_dim_input = pn.widgets.LiteralInput(value=(5, 4, 3), type=tuple, name='Room dimensions')
absorption_input = pn.widgets.FloatSlider(value=0.5, start=0.0, end=1.0, step=0.01, name='Absorption')

mic1_input = pn.widgets.LiteralInput(value=(2.5, 2, 1), type=tuple, name='Mic Position 1')
mic2_input = pn.widgets.LiteralInput(value=(2.5, 2.5, 1), type=tuple, name='Mic Position 2')
mic3_input = pn.widgets.LiteralInput(value=(2.5, 3, 1), type=tuple, name='Mic Position 3')

src1_input = pn.widgets.LiteralInput(value=(1, 1, 1.5), type=tuple, name='Source Position 1')
src2_input = pn.widgets.LiteralInput(value=(3, 1, 1.5), type=tuple, name='Source Position 2')
src3_input = pn.widgets.LiteralInput(value=(2, 1, 1.5), type=tuple, name='Source Position 3')


def update(event):
    room_dim = room_dim_input.value
    absorption = absorption_input.value

    mic_positions = {
        "mic_1": mic1_input.value,
        "mic_2": mic2_input.value,
        "mic_3": mic3_input.value
    }

    src_positions = {
        "src_1": src1_input.value,
        "src_2": src2_input.value,
        "src_3": src3_input.value
    }

    room = compute_rir(room_dim, absorption, 3, mic_positions, src_positions)
    responses = calculate_responses(room, mic_positions, src_positions)
    freq_plots = plot_freq_response(responses, mic_positions, src_positions)
    plot_pane.object = freq_plots


room_dim_input.param.watch(update, 'value')
absorption_input.param.watch(update, 'value')

mic1_input.param.watch(update, 'value')
mic2_input.param.watch(update, 'value')
mic3_input.param.watch(update, 'value')

src1_input.param.watch(update, 'value')
src2_input.param.watch(update, 'value')
src3_input.param.watch(update, 'value')

inputs = pn.Column(
    room_dim_input,
    absorption_input,
    mic1_input,
    mic2_input,
    mic3_input,
    src1_input,
    src2_input,
    src3_input
)

initial_freq_responses = compute_rir((5, 4, 3), 0.5, 3, {"mic_1": (2.5, 2, 1), "mic_2": (2.5, 2.5, 1), "mic_3": (2.5, 3, 1)}, {"src_1": (1, 1, 1.5), "src_2": (3, 1, 1.5), "src_3": (2, 1, 1.5)})
initial_plots = plot_freq_response(initial_freq_responses, {"mic_1": (2.5, 2, 1), "mic_2": (2.5, 2.5, 1), "mic_3": (2.5, 3, 1)}, {"src_1": (1, 1, 1.5), "src_2": (3, 1, 1.5), "src_3": (2, 1, 1.5)})
plot_pane = pn.pane.HoloViews(hv.Layout(initial_plots).cols(1), width=800, height=400)

pn.Row(inputs, plot_pane).servable()
# panel serve --show --autoreload panel_folder/old_main.py
# panel serve --show panel_folder/old_main.py