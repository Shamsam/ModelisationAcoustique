import tkinter as tk
from tkinter import ttk
from functools import partial

class SharedData:
    def __init__(self):
        self.mic_data = {}
        self.src_data = {}

class BaseParameters(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        base_parameters = ["Room dimensions", "Absorption", "Maximum reflection order"]
        self.base_vars = [tk.StringVar() for _ in range(len(base_parameters))]

        for index, text in enumerate(base_parameters):
            ttk.Label(self, text=text).grid(column=0, row=index, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(self, textvariable=self.base_vars[index])
            entry.grid(column=1, row=index, sticky=tk.W)

class DynamicParameters(ttk.Frame):
    def __init__(self, container, param_type, shared_data, dictionnary):
        super().__init__(container)
        self.param_type = param_type
        self.shared_data = shared_data
        self.dictionnary = dictionnary
        self.add_param_btn = ttk.Button(self, text=f"+ {param_type}", command=self.add_param)
        self.add_param_btn.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

    def add_param(self):
        index = len(self.shared_data.mic_data) if self.param_type == "Mic" else len(self.shared_data.src_data)
        text = f"{self.param_type} {index + 1}"
        label = ttk.Label(self, text=text)
        label.grid(column=0, row=index + 1, sticky=tk.W, padx=5, pady=5)
        new_var = tk.StringVar()
        entry = ttk.Entry(self, textvariable=new_var)
        entry.grid(column=1, row=index + 1, sticky=tk.W)
        btn = ttk.Button(self, text="X")
        btn.configure(command=partial(self.delete_row, label, entry, btn))
        btn.grid(column=2, row=index + 1, sticky=tk.W, padx=5)

        if self.param_type == "Mic":
            self.shared_data.mic_data[text] = new_var
        else:
            self.shared_data.src_data[text] = new_var

        self.dictionnary.update_display()

    def delete_row(self, label, entry, btn):
        text = label.cget("text")
        if self.param_type == "Mic":
            del self.shared_data.mic_data[text]
        else:
            del self.shared_data.src_data[text]

        self.dictionnary.update_display()

        label.grid_forget()
        entry.grid_forget()
        btn.grid_forget()

class DynamicDictionnary(ttk.Frame):
    def __init__(self, container, param_type, shared_data):
        super().__init__(container)
        self.param_type = param_type
        self.shared_data = shared_data
        self.update_display()

    def update_display(self):
        for child in self.winfo_children():
            child.destroy()

        data_vars = self.shared_data.mic_data.values() if self.param_type == "Mic" else self.shared_data.src_data.values()
        for index, data_var in enumerate(data_vars):
            label = ttk.Label(self, text=f"{self.param_type} {index + 1}")
            label.grid(column=0, row=index, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Label(self, textvariable=data_var)
            entry.grid(column=1, row=index, sticky=tk.W)

class RoomParametersFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        ttk.Label(self, text="Room Parameters").grid(column=0, row=0, padx=10, pady=10)
        BaseParameters(self).grid(column=0, row=1, sticky=tk.W)

class DictionnaryFrame(ttk.Frame):
    def __init__(self, container, param_type, shared_data):
        super().__init__(container)
        ttk.Label(self, text=f"{param_type} Dictionnary").grid(column=0, row=0, padx=10, pady=10)
        dictionnary = DynamicDictionnary(self, param_type, shared_data)
        dictionnary.grid(column=0, row=1, sticky=tk.W)
        DynamicParameters(self, param_type, shared_data, dictionnary).grid(column=0, row=2, sticky=tk.W)

class MainFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.create_widgets()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def create_widgets(self):
        shared_data = SharedData()
        
        RoomParametersFrame(self).grid(column=0, row=0, sticky=tk.W)
        DictionnaryFrame(self, "Mic", shared_data).grid(column=1, row=0, sticky=tk.W)
        DictionnaryFrame(self, "Src", shared_data).grid(column=1, row=1, sticky=tk.W)



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Main Frame')
        self.geometry('800x600')

if __name__ == "__main__":
    app = App()
    MainFrame(app)
    app.mainloop()




