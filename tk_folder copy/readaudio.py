import numpy as np
import librosa
from functions_ import compute_rir, calculate_responses
from plotting_fcts import plot_rir, plotting_buttons_window
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import pyfftw
from scipy.signal import stft
import scipy.fft

scipy.fft.set_backend(pyfftw.interfaces.scipy_fft)

def read_audio_file(file_path, sample_rate=32000):
    audio, _ = librosa.load(file_path, sr=sample_rate, mono=True)
    return audio


def apply_rir_to_audio(audio, rir):
    # Calculate the required size for zero-padding
    size = len(audio) + len(rir) - 1

    # Zero-pad the input signals
    audio_padded = np.pad(audio, (0, size - len(audio)))
    rir_padded = np.pad(rir, (0, size - len(rir)))

    # Compute the FFT of the zero-padded input signals
    audio_fft = scipy.fft.fft(audio_padded)
    rir_fft = scipy.fft.fft(rir_padded)

    # Compute the product of the FFTs
    product_fft = audio_fft * rir_fft

    # Compute the inverse FFT of the product
    result = scipy.fft.ifft(product_fft)

    return result.real


def process_audio_with_rir(audio_file_path=str, room_dim=list, absorption=float, max_order=int, mic_positions=dict, src_positions=dict, progress_callback=None, status_callback=None, temperature=float, humidity=float):
    if status_callback:
        status_callback("Reading audio file...")
        progress_callback(0)

    try:
        audio_signal = read_audio_file(audio_file_path)
    except Exception as e:
        print(e)
        return None, None
    
    if status_callback:
        status_callback("Computing room impulse response...")
        progress_callback(10)

    try:
        room = compute_rir(room_dim, absorption, max_order, mic_positions, src_positions, audio_signal, temperature=temperature, humidity=humidity)
    except Exception as e:
        print(e)
        return None, None

    if status_callback:
        status_callback("Calculating room impulse responses...")
        progress_callback(50)

    try:    
        rir_responses = calculate_responses(room, mic_positions, src_positions)
        mic_rirs = rir_responses["mic_1"]
    
    except Exception as e:
        print(e)
        return None, None
    
    if status_callback:
        status_callback("Plotting room impulse responses...")
        progress_callback(60)
    
    try:
        plotting_buttons_window(room)
    except Exception as e:
        print(e)
        return None, None

    if status_callback:
        progress_callback(70)
        status_callback("Applying room impulse responses to audio...")

    try:
        processed_audio = np.zeros(len(audio_signal) + len(mic_rirs[0]) - 1)
        for rir in mic_rirs:
            convolved_audio = apply_rir_to_audio(audio_signal, rir)
            if len(convolved_audio) > len(processed_audio):
                processed_audio = np.pad(processed_audio, (0, len(convolved_audio) - len(processed_audio)), 'constant')
            if len(convolved_audio) < len(processed_audio):
                convolved_audio = np.pad(convolved_audio, (0, len(processed_audio) - len(convolved_audio)), 'constant')
            processed_audio += convolved_audio
    except Exception as e:
        print(e)
        return None, None


    if status_callback:
        status_callback("Plotting processed audio...")
        progress_callback(95)

    try: 
        window = tk.Tk()
        window.title('Signal')
        

        t2 = np.arange(0, len(audio_signal)/32000, 1/32000)
        t1 = np.arange(0, len(processed_audio)/32000, 1/32000)
        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(111)
        ax.plot(t1, processed_audio, label='Processed signal', alpha=0.5)
        ax.plot(t2, audio_signal, label='Original signal', alpha=0.5)
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Amplitude')
        ax.set_title('Signal')
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas.draw()
    except Exception as e:
        print(e)
        return None, None
    
    if progress_callback:
        progress_callback(100)

    return processed_audio, room.fs
