import numpy as np
import pyroomacoustics as pra
import scipy.signal as signal
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Interactive Frequency Response Dashboard"),
    dcc.Graph(id='frequency-response-plot'),
    html.Div([
        html.Label("Absorption:"),
        dcc.Slider(id='absorption-slider', min=0, max=1, step=0.01, value=0.5, marks={i/10: f'{i/10}' for i in range(0, 11)}),
    ]),
])

@app.callback(
    Output('frequency-response-plot', 'figure'),
    Input('absorption-slider', 'value')
)
def update_plot(absorption):
    # Your provided code is placed here and modified accordingly
    # ... (all your functions and calculations)
    def calculate_frequency_response(rir, fs):
        rir_norm = rir / np.max(np.abs(rir)) # normalize the RIR
        freq, response = signal.freqz(rir_norm, fs=fs) # calculate the frequency response
        return freq, response
    
    def create_frequency_responses_figure(freq_responses, mic_positions):
        fig = go.Figure()

        for i, (freq, response) in enumerate(freq_responses):
            fig.add_trace(go.Scatter(x=freq, y=20 * np.log10(np.abs(response)), name=f'Mic Position {i}'))

        fig.update_layout(
            title="Frequency Response",
            xaxis_title="Frequency (Hz)",
            yaxis_title="Amplitude (dB)",
            legend_title="Microphone Positions",
            xaxis=dict(gridcolor='rgb(230, 230, 230)'),
            yaxis=dict(gridcolor='rgb(230, 230, 230)'),
            plot_bgcolor='rgb(255, 255, 255)',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )

        return fig

    room_dim = [5, 4, 3]
    absorption = 0.5
    room = pra.ShoeBox(room_dim, fs=16000, absorption=absorption, max_order=3)

    mic_positions = np.array([
        [2.5, 2, 1],
        [2.5, 2.5, 1],
        [2.5, 3, 1]
    ])

    src_positions = np.array([
        [1, 1, 1.5],
        [3, 1, 1.5],
        [2, 1, 1.5]
    ])

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


    return create_frequency_responses_figure(freq_responses, mic_positions)

if __name__ == '__main__':
    app.run_server(debug=True)
