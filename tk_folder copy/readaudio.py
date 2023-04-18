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
        status_callback("Calculating room impulse responses")
        progress_callback(50)

    try:    
        rir_responses = calculate_responses(room, mic_positions, src_positions)
        mic_rirs = rir_responses["mic_1"]
    except Exception as e:
        print(e)
        return None, None
    
    if status_callback:
        progress_callback(70)
        status_callback("Applying room impulse responses to audio")

    try:
        processed_audio = np.zeros(len(audio_signal) + len(mic_rirs[0]) - 1)
        for rir in mic_rirs:
            convolved_audio = apply_rir_to_audio(audio_signal, rir)
            if len(convolved_audio) > len(processed_audio):
                processed_audio = np.pad(processed_audio, (0, len(convolved_audio) - len(processed_audio)), 'constant')
            processed_audio += convolved_audio
    except Exception as e:
        print(e)
        return None, None
    
    if progress_callback:
        progress_callback(100)

    return processed_audio, room.fs, rir_responses
