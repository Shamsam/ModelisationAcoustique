import tkinter as tk
from tkinter import Toplevel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter with Matplotlib")

        # Create buttons and add them to the Tkinter window
        self.plot_sine_button = tk.Button(self, text="Plot Sine Wave", command=lambda: self.open_plot_window("sine"))
        self.plot_sine_button.pack(side=tk.TOP, padx=5, pady=5)

        self.plot_cosine_button = tk.Button(self, text="Plot Cosine Wave", command=lambda: self.open_plot_window("cosine"))
        self.plot_cosine_button.pack(side=tk.TOP, padx=5, pady=5)

    def open_plot_window(self, wave_type):
        plot_window = Toplevel(self)
        plot_window.title(f"{wave_type.capitalize()} Wave Plot")

        fig, ax = plt.subplots(figsize=(5, 4))
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Generate some example data
        x = np.linspace(0, 2 * np.pi, 100)
        if wave_type == "sine":
            y = np.sin(x)
            ax.set_title("A simple sine wave")
        elif wave_type == "cosine":
            y = np.cos(x)
            ax.set_title("A simple cosine wave")

        # Plot the data on the axes
        ax.plot(x, y)
        ax.set_xlabel("x")
        ax.set_ylabel(f"{wave_type}(x)")

        # Redraw the canvas to update the figure
        canvas.draw()


if __name__ == "__main__":
    app = App()
    app.mainloop()
