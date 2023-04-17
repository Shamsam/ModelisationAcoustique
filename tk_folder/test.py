import tkinter as tk
import tkinter.ttk as ttk
from functions_ import calculate_responses, compute_rir, plot_freq_response
import numpy as np
import scipy.signal as signal
import pyroomacoustics as pra
import matplotlib.pyplot as plt


class SharedData:
    def __init__(self):
        self.absorption = tk.DoubleVar(name="absorption_var", value=0.5)
        self.max_reflection_order = tk.IntVar(name="max_reflection_order_var", value=3)
        self.room_dimensions = (tk.DoubleVar(name="x", value=5), tk.DoubleVar(name="y", value=5), tk.DoubleVar(name="z", value=5))

        self.microphone_data = {}
        self.source_data = {}


class BaseParameters(ttk.Frame):
    def __init__(self, container, shared_data):
        super().__init__(container)
        self.abs_data = shared_data.absorption
        self.max_ref_data = shared_data.max_reflection_order
        self.room_dim_data = shared_data.room_dimensions
        self.create_scale("Absorption", self.abs_data, 0)
        self.create_widgets("Max reflection order", self.max_ref_data, 1)
        self.create_room_dim_widget("Room dimensions", self.room_dim_data, 2)

    def create_scale(self, text, variable, row):
        label = ttk.Label(self, text=text)
        label.grid(column=0, row=row, sticky=tk.W, padx=5, pady=5)
        scale = ttk.Scale(self, from_=0, to=1, variable=variable, orient=tk.HORIZONTAL, length=120)
        scale.grid(column=1, row=row, sticky=tk.W)
        variable_value = round(variable.get(), 2)
        variable.set(variable_value)
        ticklabel = ttk.Label(self, text=variable_value, width=4)
        ticklabel.grid(column=2, row=row, sticky=tk.W)

        def update_ticklabel(*args):
            ticklabel.configure(text=round(variable.get(), 2))

        variable.trace_add("write", update_ticklabel)

        
    def create_widgets(self, text, variable, row):
        label = ttk.Label(self, text=text)
        label.grid(column=0, row=row, sticky=tk.W, padx=5, pady=5)
        entry = ttk.Entry(self, textvariable=variable)
        entry.grid(column=1, row=row, sticky=tk.W)

    def create_room_dim_widget(self, text, variables, row):
        label = ttk.Label(self, text=text)
        label.grid(column=0, row=row, sticky=tk.W, padx=5, pady=5)
        self.room_dim_frame = ttk.Frame(self)
        self.room_dim_frame.grid(column=1, row=row, sticky=tk.W)
        for i, var in enumerate(variables):
            entry = ttk.Entry(master=self.room_dim_frame, textvariable=var, width=6)
            entry.grid(column=i, row=0, sticky=tk.W) 


class MicParameters(ttk.Frame): 
    def __init__(self, container, shared_data):
        super().__init__(container)
        self.mic_data = shared_data.microphone_data
        self.add_param_btn = ttk.Button(self, text="+ Mic", command=self.add_param)
        self.add_param_btn.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

    def add_param(self):
        index = 0
        while f'mic{index}' in self.mic_data:
            index += 1

        self.mic_data[f'mic{index}'] = (tk.DoubleVar(name=f"mic{index}_x"), tk.DoubleVar(name=f"mic{index}_y"), tk.DoubleVar(name=f"mic{index}_z"))
        self.create_mic_widget(f"mic{index}", self.mic_data[f'mic{index}'], index + 1)

    def create_mic_widget(self, text, variables, row):
        self.mic_grid = ttk.Frame(self)
        self.mic_grid.grid(column=0, row=row, sticky=tk.W)
        label = ttk.Label(self.mic_grid, text=text)
        label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
        mic_frame = ttk.Frame(self.mic_grid)
        mic_frame.grid(column=1, row=0, sticky=tk.W)
        for i, var in enumerate(variables):
            entry = ttk.Entry(master=mic_frame, textvariable=var, width=6)
            entry.grid(column=i, row=0, sticky=tk.W)
        btn = ttk.Button(self.mic_grid, text="X", command=lambda: self.remove_param(text))
        btn.grid(column=2, row=0, sticky=tk.W, padx=5, pady=5)
    
    def remove_param(self, text):
        index = int(text[3:])
        self.mic_data.pop(text)

        frame_to_remove = self.grid_slaves(row=index + 1, column=0)[0]
        frame_to_remove.destroy()

        for child in self.winfo_children():
            if isinstance(child, ttk.Frame) and child != self.mic_grid:
                child_index = int(child.children['!label'].cget('text')[3:])
                if child_index > index:
                    child.grid(row=child_index)


class SrcParameters(ttk.Frame):
    def __init__(self, container, shared_data):
        super().__init__(container)
        self.src_data = shared_data.source_data
        self.add_param_btn = ttk.Button(self, text="+ Src", command=self.add_param)
        self.add_param_btn.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

    def add_param(self):
        index = 0
        while f'src{index}' in self.src_data:
            index += 1

        self.src_data[f'src{index}'] = (tk.DoubleVar(name=f"src{index}_x"), tk.DoubleVar(name=f"src{index}_y"), tk.DoubleVar(name=f"src{index}_z"))
        self.create_src_widget(f"src{index}", self.src_data[f'src{index}'], index + 1)

    def create_src_widget(self, text, variables, row):
        self.src_grid = ttk.Frame(self)
        self.src_grid.grid(column=0, row=row, sticky=tk.W)
        label = ttk.Label(self.src_grid, text=text)
        label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
        src_frame = ttk.Frame(self.src_grid)
        src_frame.grid(column=1, row=0, sticky=tk.W)
        for i, var in enumerate(variables):
            entry = ttk.Entry(master=src_frame, textvariable=var, width=6)
            entry.grid(column=i, row=0, sticky=tk.W)
        btn = ttk.Button(self.src_grid, text="X", command=lambda: self.remove_param(text))
        btn.grid(column=2, row=0, sticky=tk.W, padx=5, pady=5)
    
    def remove_param(self, text):
        index = int(text[3:])
        self.src_data.pop(text)

        frame_to_remove = self.grid_slaves(row=index + 1, column=0)[0]
        frame_to_remove.destroy()

        for child in self.winfo_children():
            if isinstance(child, ttk.Frame) and child != self.src_grid:
                child_index = int(child.children['!label'].cget('text')[3:])
                if child_index > index:
                    child.grid(row=child_index)


class CalculationsParameters(ttk.Frame):
    def __init__(self, container, shared_data):
        super().__init__(container)
        self.shared_data = shared_data
        self.calculate_btn = ttk.Button(self, text="Calculate", command=self.calculate, width=30)
        self.calculate_btn.grid(column=0, row=0, sticky=tk.N, padx=5, pady=5)

    
    def calculate(self):
        self.shared_data.absorption.set(round(self.shared_data.absorption.get(), 2))
        self.new_microphone_data = {}
        self.new_source_data = {}
        for key, value in self.shared_data.microphone_data.items():
            self.new_microphone_data[key] = [value[0].get(), value[1].get(), value[2].get()]
        for key, value in self.shared_data.source_data.items():
            self.new_source_data[key] = [value[0].get(), value[1].get(), value[2].get()]

        room_dim = [self.shared_data.room_dimensions[0].get(), self.shared_data.room_dimensions[1].get(), self.shared_data.room_dimensions[2].get()]
        abs = self.shared_data.absorption.get()
        max_reflection_order = self.shared_data.max_reflection_order.get()
        mic_data = self.new_microphone_data
        src_data = self.new_source_data

        print(room_dim, abs, max_reflection_order, mic_data, src_data)

"""         room = compute_rir(room_dim, abs, max_reflection_order, mic_data, src_data)

        freq_resonses = calculate_responses(room, mic_data, src_data, norm=True, freqresp=True)

        freq_plots = plot_freq_response(freq_resonses, mic_data) """

        

        


class MainFrame(ttk.Frame):
    def __init__(self, container, shared_data):
        super().__init__(container)
        self.shared_data = shared_data
        self.base_parameters = BaseParameters(self, self.shared_data)
        self.mic_parameters = MicParameters(self, self.shared_data)
        self.src_parameters = SrcParameters(self, self.shared_data)
        self.calculations_parameters = CalculationsParameters(self, self.shared_data)
        self.base_parameters.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
        self.mic_parameters.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
        self.src_parameters.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)
        self.calculations_parameters.grid(column=1, row=0, sticky=tk.W, padx=5, pady=5)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Test")
        self.geometry("500x500")
        self.shared_data = SharedData()
        self.main_frame = MainFrame(self, self.shared_data)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()


# mettre un fichier mp3 en entrée
#fftw