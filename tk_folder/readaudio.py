import numpy as np
import librosa
from scipy import signal
from functions_ import compute_rir, calculate_responses


def read_audio_file(file_path, sample_rate=16000):
    audio, _ = librosa.load(file_path, sr=sample_rate, mono=True)
    return audio


def apply_rir_to_audio(audio, rir):
        return signal.convolve(audio, rir, mode="full")


def process_audio_with_rir(audio_file_path=str, room_dim=list, absorption=float, max_order=int, mic_positions=dict, src_positions=dict, progress_callback=None, status_callback=None):
    '''Process audio file with room impulse response
    
    Parameters
    ----------
    audio_file_path : str
        The path to the audio file.
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
    progress_callback : function, optional
        The function to call when progress is updated.
    status_callback : function, optional
        The function to call when status is updated.
    '''
    if status_callback:
        status_callback("Reading audio file")
        progress_callback(0)

    try:
        audio_signal = read_audio_file(audio_file_path)
    except Exception as e:
        print(e)
        return None, None
    
    if status_callback:
        status_callback("Computing room impulse response")
        progress_callback(10)

    try:
        room = compute_rir(room_dim, absorption, max_order, mic_positions, src_positions)
    except Exception as e:
        print(e)
        return None, None

    if status_callback:
        status_callback("Calculating combined room impulse response")
        progress_callback(50)

    try:    
        comb_imp_responses = calculate_responses(room, mic_positions, src_positions, norm=True, freqresp=False)
        combined_rir = comb_imp_responses["mic_1"]
    except Exception as e:
        print(e)
        return None, None
    
    if status_callback:
        progress_callback(70)
        status_callback("Applying room impulse response to audio")
    try:
        processed_audio = apply_rir_to_audio(audio_signal, combined_rir)
    except Exception as e:
        print(e)
        return None, None
    
    if progress_callback:
        progress_callback(100)  # Set progress to 100% when calculations are complete

    return processed_audio, room.fs


