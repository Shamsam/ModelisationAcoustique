import tkinter as tk
from tkinter import Toplevel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np


def plot_rirs(self, rir_responses, mic_positions):
    #   rir_responses : dict
    #   The dict of room impulse responses.
    #   format: {"mic_1": [rir_1, rir_2, ...], "mic_2": [rir_1, rir_2, ...], ...}
    plot_window = Toplevel(self)
    plot_window.title("Room Impulse Responses")

    fig, ax = plt.subplots(figsize=(8, 6))
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Plot the data on the axes
    for mic in mic_positions:
        for rir in rir_responses[mic]:
            ax.plot(rir)

    ax.set_xlabel("Time [samples]")
    ax.set_ylabel("Amplitude")
    ax.set_title("Room Impulse Responses")

    canvas.draw()




    