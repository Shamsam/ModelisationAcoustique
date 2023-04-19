import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

def plot_rir(rir, fs, src):
    """Plot the room impulse response.

    Parameters
    ----------
    rir : ndarray
        The room impulse response.

    Returns
    -------
    None

    """

    # Create a new window for the plot
    plot_window = tk.Toplevel()
    plot_window.title("Room Impulse Response")

    # Create a new figure and axes for the plot
    fig, ax = plt.subplots(figsize=(8, 6))

    # Compute the time axis for the plot
    t = np.arange(len(rir)) / fs  # assuming a sample rate of 16000 Hz

    # Plot the room impulse response on the axes
    ax.plot(t, rir)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Room Impulse Response of mic1 and " + str(src))

    # Create a canvas for the plot and add it to the window
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Redraw the canvas to update the figure
    canvas.draw()