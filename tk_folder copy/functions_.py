import numpy as np
import scipy.signal as signal
import pyroomacoustics as pra
import matplotlib.pyplot as plt


def freq_resp(room: pra.ShoeBox, norm_ir):
    """Compute the frequency response of the room impulse response.\n
    **NOT OFFICIAL pyroomacoustics function**

    Parameters
    ----------
    room : pyroomacoustics.ShoeBox
        The room object.
    norm_ir : ndarray
        The normalized and combined room impulse response.

    Returns
    -------
    freq_response : tuple
        The frequency response of the room impulse response.
        format : (freq, response)
            
    """

    freq, response = signal.freqz(norm_ir, fs=room.fs)
    freq_response = (freq, response)
    return freq_response


def compute_rir(room_dim, absorption, max_order: int, mic_positions: dict, src_positions: dict):
    """Compute the room impulse response of the room.\n
    **NOT OFFICIAL pyroomacoustics function**

    Parameters
    ----------
    room_dim : list
        The dimensions of the room.
    absorption : float
        The absorption coefficient of the room.
    max_order : int
        The maximum reflection order of the room.
    mic_positions : dict
        The microphone positions.
        format: {"mic_1": [x1, y1, z1], "mic_2": [x2, y2, z2], ...}
    src_positions : dict
        The source positions.
        format: {"src_1": [x1, y1, z1], "src_2": [x2, y2, z2], ...}

    Returns
    -------
    room : pyroomacoustics.Room
        The room object and its properties.
        Access the room impulse response: room.rir[mic_idx][src_idx]
    
    """

    room = pra.ShoeBox(room_dim, fs=16000, absorption=absorption, max_order=max_order, ray_tracing=True, use_rand_ism=True)    
    for src_pos in src_positions.values():
        room.add_source(src_pos)

    for mic_pos in mic_positions.values():
        room.add_microphone_array(pra.MicrophoneArray(np.array([mic_pos]).T, room.fs))


    room.compute_rir()

    return room


def calculate_responses(room: pra.ShoeBox, mic_positions: dict, src_positions: dict):
    """Calculate the room impulse response and the frequency response.\n
    **NOT OFFICIAL pyroomacoustics function**

    Parameters
    ----------
    room : pyroomacoustics.Room
        The room object and its properties.
        Access the room impulse response: room.rir[mic_idx][src_idx]
    mic_positions : dict
        The microphone positions.
        format: {"mic_1": [x1, y1, z1], "mic_2": [x2, y2, z2], ...}
    src_positions : dict
        The source positions.
        format: {"src_1": [x1, y1, z1], "src_2": [x2, y2, z2], ...}

    Returns
    -------
    rir_responses : dict
        The dict of room impulse responses.
        format: {"mic_1": [rir_1, rir_2, ...], "mic_2": [rir_1, rir_2, ...], ...}
    """

    rir_responses = {}
    for mic_idx in range(len(mic_positions)):
        rir_responses[f"mic_{mic_idx + 1}"] = [room.rir[mic_idx][src_idx] for src_idx in range(len(src_positions))]
    return rir_responses

def plot_freq_response(freq_responses: dict, mic_positions: dict):
    """Plot the frequency response of the room impulse response.\n
    **NOT OFFICIAL pyroomacoustics function**

    Parameters
    ----------
    freq_responses : dict
        The dict of frequency responses.
        format: {"mic_1": (freq, response), "mic_2": (freq, response), ...}
    mic_positions : dict
        The microphone positions.
        format: {"mic_1": [x1, y1, z1], "mic_2": [x2, y2, z2], ...}

    Returns
    -------
    freq_plots : list
        The list of frequency plots.
        format: [plt.plot(freq, 20 * np.log10(np.abs(response)), label=f"mic_{mic_idx + 1}"), ...]
    """
    freq_plots = []
    for mic_idx in range(len(mic_positions)):
        freq, response = freq_responses[f"mic_{mic_idx + 1}"]
        freq_plots.append(plt.plot(freq, 20 * np.log10(np.abs(response)), label=f"mic_{mic_idx + 1}"))
        
    return freq_plots