import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.signal import stft
import pyroomacoustics as pra
from scipy.signal import freqz

def plotting_buttons_window(room: pra.Room):
    """Create a new window for the plotting buttons.

    Returns
    -------
    None

    """
    mic = 0
    max_rir_len = max(len(room.rir[mic][src_idx]) for src_idx in range(len(room.sources)))
    # Create a new window for the plotting buttons
    plotting_buttons_window = tk.Toplevel()
    plotting_buttons_window.title("Plotting Buttons")

    # Create a button for plotting the room impulse response
    plot_rir_button = tk.Button(master=plotting_buttons_window, text="Plot Room Impulse Response", command= lambda: plot_rir(room, mic, max_rir_len))
    plot_rir_button.pack()

    # Create a button for plotting the frequency response
    plot_freq_resp_button = tk.Button(master=plotting_buttons_window, text="Plot Frequency Response", command= lambda: plot_freq_resp(room, max_rir_len))
    plot_freq_resp_button.pack()

    # Create a button for plotting the spectrogram
    plot_spectrogram_button = tk.Button(master=plotting_buttons_window, text="Plot Spectrogram", command= lambda: plot_spectrogram(room, max_rir_len))
    plot_spectrogram_button.pack()


def plot_rir(room: pra.Room, mic: int, max_rir_len: int):
    """Plot the room impulse response.
    
    Parameters
    ----------
    room : pyroomacoustics.Room
        The room object and its properties.
        Access the room impulse response: room.rir[mic_idx][src_idx]
    mic : int
        The microphone index.
    max_rir_len : int
        The maximum length of the room impulse response.

    Returns
    -------
    None

    """
    print('Starting...')

    # Create a new window for the plot
    plot_window = tk.Toplevel()
    plot_window.title("Room Impulse Response")

    # Create a new figure and axes for the plot
    fig, ax = plt.subplots(figsize=(8, 6))
    # Compute the time axis for the plot
    t = np.arange(max_rir_len) / room.fs

    # Plot the room impulse response on the axes
    try:
        for src_idx, source in enumerate(room.sources):
            # pad the rir with zeros if it is shorter than the longest rir
            if len(room.rir[mic][src_idx]) < max_rir_len:
                room.rir[mic][src_idx] = np.pad(room.rir[mic][src_idx], (0, max_rir_len - len(room.rir[mic][src_idx])), 'constant')
            ax.plot(t, room.rir[mic][src_idx], label="Source " + str(src_idx))
    except Exception as e:
        print(e)
        print('Error in plotting the room impulse response')

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Room Impulse Response of mic" + str(mic))
    ax.legend()
    ax.grid(True)  # add grid lines

    # Create a canvas for the plot and add it to the window
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    # Redraw the canvas to update the figure
    canvas.draw()


def plot_freq_resp(room: pra.Room, max_rir_len: int):
    """Plot the frequency response.

    Parameters
    ----------
    room : pyroomacoustics.Room
        The room object and its properties.
        Access the room impulse response: room.rir[mic_idx][src_idx]
    max_rir_len : int
        The maximum length of the room impulse response.

    Returns
    -------
    None

    """
    print('Starting...')
    # Create a new window for the plot
    plot_window = tk.Toplevel()
    plot_window.title("Frequency Response")

    # Create a new figure and axes for the plot
    fig, ax = plt.subplots(figsize=(8, 6))

    try:
        # Plot the frequency response on the axes
        for src_idx, source in enumerate(room.sources):
            if len(room.rir[0][src_idx]) < max_rir_len:
                room.rir[0][src_idx] = np.pad(room.rir[0][src_idx], (0, max_rir_len - len(room.rir[0][src_idx])), 'constant')
            print('Computing the frequency response...')
            rir = room.rir[0][src_idx] / np.max(np.abs(room.rir[0][src_idx]))
            freq, resp = freqz(rir)
            freq = freq / (2 * np.pi) * room.fs
            ax.semilogx(freq, 20 * np.log10(np.abs(resp)), label="Source " + str(src_idx))
    except Exception as e:
        print(e)
        print('Error in plotting the frequency response')
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Amplitude (dB)")
    ax.set_title("Frequency Response of mic0")
    ax.legend()
    ax.grid(True)  # add grid lines

    # Create a canvas for the plot and add it to the window
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Redraw the canvas to update the figure
    canvas.draw()
    print('Done!')




def plot_spectrogram(room: pra.Room, max_rir_len: int, nperseg=256, noverlap=None, cmap='inferno'):
    """
    Plots spectrograms for each source-microphone pair in a pyroomacoustics room object.

    Parameters:
    room (pyroomacoustics.room.Room): The room object with precomputed RIRs.
    nperseg (int, optional): Number of samples per segment for the STFT. Default is 256.
    noverlap (int, optional): Number of samples to overlap between segments. Default is nperseg // 2.
    cmap (str, optional): Colormap for the spectrograms. Default is 'inferno'.
    """
    print('Starting...')
    if noverlap is None:
        noverlap = nperseg // 2

    # Create a new window for the plot
    plot_window = tk.Toplevel()
    plot_window.title("Spectrogram")

    # Create a new figure and axes for the plot
    fig, ax = plt.subplots(figsize=(8, 6))
    try:
        # Plot the spectrogram on the axes
        for src_idx, source in enumerate(room.sources):
            if len(room.rir[0][src_idx]) < max_rir_len:
                room.rir[0][src_idx] = np.pad(room.rir[0][src_idx], (0, max_rir_len - len(room.rir[0][src_idx])), 'constant')
            f, t, Sxx = stft(room.rir[0][src_idx], room.fs, nperseg=nperseg, noverlap=noverlap)
            pcm = ax.pcolormesh(t, f, 20 * np.log10(np.abs(Sxx)), cmap=cmap, shading='gouraud')
    except Exception as e:
        print(e)
        print('Error in plotting the spectrogram')

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    ax.set_yscale('log')  # use logarithmic scale for the frequency axis
    ax.set_title("Spectrogram of mic0")
    ax.legend()
    ax.grid(True)  # add grid lines

    # Create a colorbar for the intensity scale
    fig.colorbar(pcm, ax=ax, label="Magnitude (dB)")

    # Create a canvas for the plot and add it to the window
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Redraw the canvas to update the figure
    canvas.draw()

    print('Done!')
