import tkinter as tk
import tkinter.ttk as ttk
from functools import partial



class SharedData:
    def __init__(self):
        self.absorption = tk.IntVar(name="absorption")
        self.max_reflection_order = tk.IntVar(name="max_reflection_order")
        self.room_dimensions = (tk.IntVar(name="x"), tk.IntVar(name="y"), tk.IntVar(name="z"))

        self.microphone_data = {}
        self.source_data = {}


class BaseParameters(ttk.Frame):
    def __init__(self, container, shared_data):
        super().__init__(container)
        self.abs_data = shared_data.absorption
        self.max_ref_data = shared_data.max_reflection_order
        self.room_dim_data = shared_data.room_dimensions
        self.create_widgets("Absorption", self.abs_data, 0)
        self.create_widgets("Max reflection order", self.max_ref_data, 1)
        self.create_room_dim_widget("Room dimensions", self.room_dim_data, 2)
        
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
        if len(self.mic_data) == 0:
            index = 0
        else:
            index = int(list(self.mic_data.keys())[-1][-1]) + 1

        self.mic_data[f'mic{index}'] = (tk.IntVar(name=f"mic{index}_x"), tk.IntVar(name=f"mic{index}_y"), tk.IntVar(name=f"mic{index}_z"))
        self.create_mic_widget(f"mic{index}", self.mic_data[f'mic{index}'], len(self.mic_data))

    def create_mic_widget(self, text, variables, row):
        label = ttk.Label(self, text=text)
        label.grid(column=0, row=row, sticky=tk.W, padx=5, pady=5)
        self.mic_frame = ttk.Frame(self)
        self.mic_frame.grid(column=1, row=row, sticky=tk.W)
        for i, var in enumerate(variables):
            entry = ttk.Entry(master=self.mic_frame, textvariable=var, width=6)
            entry.grid(column=i, row=0, sticky=tk.W)

        

class SrcParameters(ttk.Frame):
    def __init__(self, container, shared_data):
        super().__init__(container)
        self.src_data = shared_data.source_data
        self.add_param_btn = ttk.Button(self, text="+ Src", command=self.add_param)
        self.add_param_btn.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

    def add_param(self): 
        try: 
            index = int(list(self.src_data.keys())[-1][-1]) + 1

        except IndexError:
            index = 0

        self.src_data[f'src{index}'] = (tk.IntVar(name=f"src{index}_x"), tk.IntVar(name=f"src{index}_y"), tk.IntVar(name=f"src{index}_z"))
        self.create_src_widget(f"src{index}", self.src_data[f'src{index}'], len(self.src_data))

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
    
    def remove_param(self, text): # here is how to remove the correct widget
        self.src_data.pop(text)
        for child in self.src_grid.winfo_children():
            child.destroy()
        self.src_grid.destroy()



class MainFrame(ttk.Frame):
    def __init__(self, container, shared_data):
        super().__init__(container)
        self.shared_data = shared_data
        self.base_parameters = BaseParameters(self, self.shared_data)
        self.mic_parameters = MicParameters(self, self.shared_data)
        self.src_parameters = SrcParameters(self, self.shared_data)
        self.base_parameters.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
        self.mic_parameters.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
        self.src_parameters.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)




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