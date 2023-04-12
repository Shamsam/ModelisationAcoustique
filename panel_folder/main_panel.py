import pyroomacoustics as pra
import matplotlib.pyplot as plt
import scipy.signal as signal
import panel as pn
import param
import holoviews as hv
import numpy as np
from response_calculations import freq_resp, compute_rir, calculate_responses

pn.extension()
hv.extension("bokeh")

class RoomResponse(param.Parameterized):
    room_dim = param.List(default=[5, 4, 3])
    absorption = param.Number(default=0.5, bounds=(0, 1))
    max_order = param.Integer(default=3, bounds=(0, None))

    def __init__(self, **params):
        super().__init__(**params)
        self.mic_positions = {
            "mic_1": [2.5, 2, 1],
            "mic_2": [2.5, 2.5, 1],
            "mic_3": [2.5, 3, 1]
        }

        self.src_positions = {
            "src_1": [1, 1, 1.5],
            "src_2": [3, 1, 1.5],
            "src_3": [2, 1, 1.5]
        }

        self.room = compute_rir(self.room_dim, self.absorption, self.max_order, self.mic_positions, self.src_positions)
        self.freq_responses = calculate_responses(self.room, self.mic_positions, self.src_positions)

    @param.depends("room_dim", "absorption", "max_order", watch=True)
    def update_responses(self):
        self.room = compute_rir(self.room_dim, self.absorption, self.max_order, self.mic_positions, self.src_positions)
        self.freq_responses = calculate_responses(self.room, self.mic_positions, self.src_positions)

    @param.depends("room_dim", "absorption", "max_order")
    def plot_responses(self):
        hv_plot = hv.Overlay()

        for mic_idx in range(len(self.mic_positions)):
            freq, response = self.freq_responses[f"mic_{mic_idx + 1}"]
            response_db = 20 * np.log10(np.abs(response))
            hv_plot *= hv.Curve((freq, response_db), label=f"mic_{mic_idx + 1}")

        hv_plot.opts(xlabel="Frequency (Hz)", ylabel="Response (dB)", title="Frequency Response", width=800, height=500)
        return hv_plot


room_response = RoomResponse()
params_panel = pn.Param(room_response, parameters=["room_dim", "absorption", "max_order"], show_name=False, width=300)
response_plot = pn.panel(room_response.plot_responses)

pn.Row(params_panel, response_plot).servable()

# panel serve --show --autoreload panel_folder/main_panel.py