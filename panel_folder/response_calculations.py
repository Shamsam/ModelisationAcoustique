import numpy as np
import scipy.signal as signal
import pyroomacoustics as pra


def freq_resp(room: pra.Room, norm_ir):
    """Compute the frequency response of the room impulse response.\n
    **NOT OFFICIAL pyroomacoustics function**

    Parameters
    ----------
    room : pyroomacoustics.Room
        The room object.
    norm_ir : ndarray
        The normalized room impulse response.

    Returns
    -------
    freq_response : tuple
        The frequency response of the room impulse response.
        (freq, response)
    
    """
    freq, response = signal.freqz(norm_ir, fs=room.fs)
    freq_response = (freq, response)
    return freq_response


def compute_rir(room_dim, absorption, max_order, mic_positions, src_positions):
    """Compute the room impulse response of the room.\n
    **NOT OFFICIAL pyroomacoustics function**

    Parameters
    ----------
    room_dim : tuple
        The dimensions of the room.
    absorption : float
        The absorption coefficient of the room.
    max_order : int
        The maximum reflection order of the room.
    mic_positions : array
        The microphone positions.
        format: [[x1, y1, z1], [x2, y2, z2], ...]
    src_positions : array
        The source positions.
        format: [[x1, y1, z1], [x2, y2, z2], ...]

    Returns
    -------
    room : pyroomacoustics.Room
        The room object and its properties.
        Access the room impulse response: room.rir[mic_idx][src_idx]
    
    """

    room = pra.ShoeBox(room_dim, fs=16000, absorption=absorption, max_order=max_order)    
    for src_pos in src_positions:
        room.add_source(src_pos)

    for mic_pos in mic_positions:
        room.add_microphone(mic_pos)

    room.compute_rir()
    return room

def calculate_responses(room: pra.ShoeBox, mic_positions, src_positions):
    """Compute the frequency response of the room impulse response.\n
    **NOT OFFICIAL pyroomacoustics function**

    Parameters
    ----------
    room : pyroomacoustics.Room
        The room object.
        Access the room impulse response: room.rir[mic_idx][src_idx]
    mic_positions : array
        The microphone positions.
        format: [[x1, y1, z1], [x2, y2, z2], ...]
    src_positions : array
        The source positions.
        format: [[x1, y1, z1], [x2, y2, z2], ...]

    Returns
    -------
    freq_responses : dict
        The dict of frequency responses.
        format: {"mic_1": (freq, response), "mic_2": (freq, response), ...}
        to access the frequency response in loops: freq_responses[f"mic_{mic_idx + 1}"]
    
    """

    freq_responses = {}
    for mic_idx in range(len(mic_positions)):
        max_rir_len = max(len(room.rir[mic_idx][src_idx]) for src_idx in range(len(src_positions)))
        combined_rir = sum(np.resize(room.rir[mic_idx][src_idx], max_rir_len) for src_idx in range(len(src_positions)))
        freq, response = freq_resp(room, combined_rir)
        freq_responses[f"mic_{mic_idx + 1}"] = (freq, response)


    return freq_responses

#to do: in compute_rir, also create new mic_positions and src_positions dictionaries with the same length as the number of mics and sources