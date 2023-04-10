import numpy as np
import scipy.signal as signal
import pyroomacoustics as pra


def freq_resp(room, norm_ir):
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
    mic_positions : list
        The list of microphone positions.
    src_positions : list
        The list of source positions.

    Returns
    -------
    mic_positions : list
        The list of microphone positions.
    src_positions : list
        The list of source positions.
    room : pyroomacoustics.Room
        The room object.
    
    """

    room = pra.ShoeBox(room_dim, fs=16000, absorption=absorption, max_order=max_order)    
    for src_pos in src_positions:
        room.add_source(src_pos)

    for mic_pos in mic_positions:
        room.add_microphone(mic_pos)

    room.compute_rir()
    return mic_positions, src_positions, room

def calculate_responses(room, mic_positions, src_positions):
    """Compute the frequency response of the room impulse response.\n
    **NOT OFFICIAL pyroomacoustics function**

    Parameters
    ----------
    room : pyroomacoustics.Room
        The room object.
    mic_positions : list
        The list of microphone positions.
    src_positions : list
        The list of source positions.

    Returns
    -------
    freq_responses : list
        The list of frequency responses.
            [(freq, response), (freq, response), ...]
    
    """

    freq_responses = []
    for mic_idx, _ in enumerate(mic_positions):
        max_rir_len = max(len(room.rir[mic_idx, src_idx]) for src_idx, _ in enumerate(src_positions))
        combined_rir = sum(np.resize(room.rir[mic_idx, src_idx], max_rir_len) for src_idx, _ in enumerate(src_positions))
        freq, response = freq_resp(combined_rir, room.get_fs())
        freq_responses.append((freq, response))

    return freq_responses