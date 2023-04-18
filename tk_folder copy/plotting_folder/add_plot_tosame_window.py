import tkinter as tk
from tkinter import Toplevel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter with Matplotlib")

        self.plot_sine_button = tk.Button(self, text="Plot Sine Wave", command=lambda: self.open_plot_window("sine"))
        self.plot_sine_button.pack(side=tk.TOP, padx=5, pady=5)

        self.plot_cosine_button = tk.Button(self, text="Plot Cosine Wave", command=lambda: self.open_plot_window("cosine"))
        self.plot_cosine_button.pack(side=tk.TOP, padx=5, pady=5)

        self.add_tan_button = tk.Button(self, text="Add Tangent Plot", command=self.add_tangent_plot)
        self.add_tan_button.pack(side=tk.TOP, padx=5, pady=5)

        self.figure = None
        self.plot_window = None
        self.canvas = None
        self.subplot_index = 1

    def open_plot_window(self, wave_type):
        if self.plot_window is None:
            self.plot_window = Toplevel(self)
            self.plot_window.title("Wave Plot")
            self.figure = plt.figure(figsize=(5, 4))
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_window)
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            self.plot_window.protocol("WM_DELETE_WINDOW", self.clear_plot_window)

        x = np.linspace(0, 2 * np.pi, 100)
        if wave_type == "sine":
            ax = self.figure.add_subplot(1, 3, self.subplot_index)
            y = np.sin(x)
            ax.plot(x, y)
            ax.set_title("Sine wave")
            self.subplot_index += 1
        elif wave_type == "cosine":
            ax = self.figure.add_subplot(1, 3, self.subplot_index)
            y = np.cos(x)
            ax.plot(x, y)
            ax.set_title("Cosine wave")
            self.subplot_index += 1

        self.canvas.draw()

    def clear_plot_window(self):
        self.plot_window.destroy()
        self.plot_window = None
        self.figure = None
        self.canvas = None
        self.subplot_index = 1

    def add_tangent_plot(self):
        if self.plot_window is not None and self.subplot_index < 4:
            x = np.linspace(0, 2 * np.pi, 100)
            y = np.tan(x)
            ax = self.figure.add_subplot(1, 3, self.subplot_index)
            ax.plot(x, y)
            ax.set_title("Tangent wave")
            self.subplot_index += 1
            self.canvas.draw()


if __name__ == "__main__":
    app = App()
    app.mainloop()
