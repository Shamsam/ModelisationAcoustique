import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import sounddevice as sd
from readaudio import process_audio_with_rir
import soundfile as sf
from readaudio import read_audio_file
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SharedData:
    def __init__(self):
        self.absorption = tk.DoubleVar(name="absorption_var", value=0.5)
        self.max_reflection_order = tk.IntVar(name="max_reflection_order_var", value=3)
        self.room_dimensions = (tk.DoubleVar(name="x", value=5), tk.DoubleVar(name="y", value=5), tk.DoubleVar(name="z", value=5))
        self.humidity = tk.DoubleVar(name="humidity", value=0)
        self.temperature = tk.DoubleVar(name="temperature", value=20)
        

        self.microphone_data = {}
        self.source_data = {}
        self.file_path = tk.StringVar(name="file_path", value="")
        self.audio_data = tk.StringVar(name="audio_data", value="")
        self.fs = tk.IntVar(name="fs", value=32000)


class BaseParameters(ttk.Frame):
    def __init__(self, container, shared_data):
        super().__init__(container)
        self.shared_data = shared_data
        shared_data.base_parameters = self
        self.abs_data = shared_data.absorption
        self.max_ref_data = shared_data.max_reflection_order
        self.room_dim_data = shared_data.room_dimensions
        self.humidity_data = shared_data.humidity
        self.temperature_data = shared_data.temperature
        self.create_scale("Absorption", self.abs_data, 0)
        self.create_widgets("Max reflection order", self.max_ref_data, 1)
        self.create_widgets("Humidity", self.humidity_data, 2)
        self.create_widgets("Temperature", self.temperature_data, 3)
        self.create_room_dim_widget("Room dimensions", self.room_dim_data, 4)
        self.create_room_visualization()

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
        
    def create_room_visualization(self):
        room_visualization = tk.Toplevel()
        room_visualization.title("Room visualization")
        canvas_width = 1000
        canvas_height = 500
        max_room_size = 20  # Adjust this based on the maximum room size you expect

        self.room_canvas = tk.Canvas(room_visualization, width=canvas_width, height=canvas_height)
        self.room_canvas.pack()

        def update_room_visualization(*args):
            self.room_canvas.delete("all")

            x = self.room_dim_data[0].get() * (canvas_width / 2) / max_room_size
            y = self.room_dim_data[1].get() * (canvas_height / 2) / max_room_size
            z = self.room_dim_data[2].get() * (canvas_height / 2) / max_room_size

            # Top view
            self.room_canvas.create_rectangle(50, 50, 50 + x, 50 + y, outline="black", fill="white", tags="top_view")
            self.room_canvas.create_text(50 + x / 2, 40, text=f"X: {self.room_dim_data[0].get()}", tags="top_view_label")
            self.room_canvas.create_text(30, 50 + y / 2, text=f"Y: {self.room_dim_data[1].get()}", tags="top_view_label", angle=90)

            # Side view
            self.room_canvas.create_rectangle(50 + x + 20, 50, 50 + x + 20 + x, 50 + z, outline="black", fill="white", tags="side_view")
            self.room_canvas.create_text(50 + x + 20 + x / 2, 40, text=f"X: {self.room_dim_data[0].get()}", tags="side_view_label")
            self.room_canvas.create_text(50 + x + 10, 50 + z / 2, text=f"Z: {self.room_dim_data[2].get()}", tags="side_view_label", angle=90)

            # Draw microphones
            for mic_vars in self.shared_data.microphone_data.values():
                mic_x = mic_vars[0].get() * (canvas_width / 2) / max_room_size
                mic_y = mic_vars[1].get() * (canvas_height / 2) / max_room_size
                mic_z = mic_vars[2].get() * (canvas_height / 2) / max_room_size

                # Microphone in top view
                self.room_canvas.create_oval(50 + mic_x - 3, 50 + mic_y - 3, 50 + mic_x + 3, 50 + mic_y + 3, fill="red", tags="mic_top_view")

                # Microphone in side view
                self.room_canvas.create_oval(50 + x + 20 + mic_x - 3, 50 + mic_z - 3, 50 + x + 20 + mic_x + 3, 50 + mic_z + 3, fill="red", tags="mic_side_view")

            # Draw sources
            for src_vars in self.shared_data.source_data.values():
                src_x = src_vars[0].get() * (canvas_width / 2) / max_room_size
                src_y = src_vars[1].get() * (canvas_height / 2) / max_room_size
                src_z = src_vars[2].get() * (canvas_height / 2) / max_room_size

                # Source in top view
                self.room_canvas.create_oval(50 + src_x - 3, 50 + src_y - 3, 50 + src_x + 3, 50 + src_y + 3, fill="blue", tags="src_top_view")

                # Source in side view
                self.room_canvas.create_oval(50 + x + 20 + src_x - 3, 50 + src_z - 3, 50 + x + 20 + src_x + 3, 50 + src_z + 3, fill="blue", tags="src_side_view")

        for var in self.room_dim_data:
            var.trace_add("write", update_room_visualization)

        for mic_vars in self.shared_data.microphone_data.values():
            for mic_var in mic_vars:
                mic_var.trace_add("write", update_room_visualization)

        update_room_visualization()
    
    def update_src_traces(self):
        for src_vars in self.shared_data.source_data.values():
            for src_var in src_vars:
                # Remove existing trace
                try:
                    src_var.trace_remove("write", src_var.trace_info()[0][1])
                except IndexError:
                    pass

                # Add new trace
                src_var.trace_add("write", self.update_room_visualization)

    def update_mic_traces(self):
        for mic_vars in self.shared_data.microphone_data.values():
            for mic_var in mic_vars:
                # Remove existing trace
                try:
                    mic_var.trace_remove("write", mic_var.trace_info()[0][1])
                except IndexError:
                    pass

                # Add new trace
                mic_var.trace_add("write", self.update_room_visualization)
        

class MicParameters(ttk.Frame): 
    def __init__(self, container, shared_data):
        super().__init__(container)
        self.shared_data = shared_data
        self.mic_data = shared_data.microphone_data
        self.add_param_btn = ttk.Button(self, text="+ Mic", command=self.add_param)
        self.add_param_btn.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

    def add_param(self):
        index = 0
        while f'mic{index}' in self.mic_data:
            index += 1

        self.mic_data[f'mic{index}'] = (tk.DoubleVar(name=f"mic{index}_x", value=2), tk.DoubleVar(name=f"mic{index}_y", value=2), tk.DoubleVar(name=f"mic{index}_z", value=2))
        self.create_mic_widget(f"mic{index}", self.mic_data[f'mic{index}'], index + 1)
        self.update_mic_traces()

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
        self.update_mic_traces()

    def update_mic_traces(self):
        self.shared_data.base_parameters.update_mic_traces()


class SrcParameters(ttk.Frame):
    def __init__(self, container, shared_data):
        super().__init__(container)
        self.shared_data = shared_data
        self.src_data = shared_data.source_data
        self.add_param_btn = ttk.Button(self, text="+ Src", command=self.add_param)
        self.add_param_btn.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

    def add_param(self):
        index = 0
        while f'src{index}' in self.src_data:
            index += 1

        self.src_data[f'src{index}'] = (tk.DoubleVar(name=f"src{index}_x", value=4), tk.DoubleVar(name=f"src{index}_y", value=4), tk.DoubleVar(name=f"src{index}_z", value=4))
        self.create_src_widget(f"src{index}", self.src_data[f'src{index}'], index + 1)
        self.update_src_traces()

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
        self.update_src_traces()

    def update_src_traces(self):
        self.shared_data.base_parameters.update_src_traces()


class FileFrame(ttk.Frame):
    def __init__(self, container, shared_data):
        super().__init__(container)
        self.shared_data = shared_data
        self.file_path = tk.StringVar()
        self.file_path.set("No file selected")
        self.file_path_label = ttk.Label(self, textvariable=self.file_path)
        self.file_path_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
        self.file_btn = ttk.Button(self, text="Select file", command=self.select_file)
        self.file_btn.grid(column=1, row=0, sticky=tk.W, padx=5, pady=5)
        self.play_btn = ttk.Button(self, text="Play", command=self.play_audio)
        self.play_btn.grid(column=2, row=0, sticky=tk.W, padx=5, pady=5)

    def select_file(self):
        self.file_path.set(filedialog.askopenfilename())
        self.shared_data.file_path.set(self.file_path.get())
        audio_data = read_audio_file(self.file_path.get())
        self.shared_data.audio_data = audio_data
        self.shared_data.fs = 32000

    def play_audio(self):
        if self.file_path.get() != "No file selected":
            try:
                print('Playing audio...')
                audio_data = (self.shared_data.audio_data)
                sd.play(audio_data, self.shared_data.fs)
                sd.wait()
                print('Audio played!')
            except Exception as e:
                print(e)
        else:
            messagebox.showerror("Error", "No file selected")


class CalculationsParameters(ttk.Frame):
    def __init__(self, container, shared_data):
        super().__init__(container)
        self.shared_data = shared_data
        self.set_parameters_btn = ttk.Button(self, text="Set Parameters", command=self.get_vars, width=30)
        self.set_parameters_btn.grid(column=0, row=0, sticky=tk.N, padx=5, pady=5)
        self.calculate_btn = ttk.Button(self, text="Calculate", command=self.process_audio, width=30)
        self.calculate_btn.grid(column=0, row=1, sticky=tk.N, padx=5, pady=5)

        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.grid(column=0, row=2, padx=5, pady=5)

        self.status_text = tk.StringVar()
        self.status_label = ttk.Label(self, textvariable=self.status_text)
        self.status_label.grid(column=0, row=3, padx=5, pady=5)

        self.play_btn = ttk.Button(self, text="Play", command=self.play_audio, width=30)
        self.play_btn.grid(column=0, row=4, sticky=tk.N, padx=5, pady=5)

    
    def get_vars(self):
        print('reading vars...')
        self.shared_data.absorption.set(round(self.shared_data.absorption.get(), 2))
        self.mic_data = {}
        self.src_data = {}
        for key, value in self.shared_data.microphone_data.items():
            self.mic_data[key] = [value[0].get(), value[1].get(), value[2].get()]
        for key, value in self.shared_data.source_data.items():
            self.src_data[key] = [value[0].get(), value[1].get(), value[2].get()]

        self.room_dim = [self.shared_data.room_dimensions[0].get(), self.shared_data.room_dimensions[1].get(), self.shared_data.room_dimensions[2].get()]
        self.abs = self.shared_data.absorption.get()
        self.max_reflection_order = self.shared_data.max_reflection_order.get()
        self.file_path = self.shared_data.file_path.get()
        self.temperature = self.shared_data.temperature.get()
        self.humidity = self.shared_data.humidity.get()
        print('Retreived vars!')

    def update_progress(self, value):
        self.progress['value'] = value
        self.update_idletasks()

    def update_status(self, status):
        self.status_text.set(status)

    def process_audio(self):
        print('processing audio...')
        try:
            processed_audio, sample_rate = process_audio_with_rir(self.file_path, self.room_dim, self.abs, self.max_reflection_order, self.mic_data, self.src_data, progress_callback=self.update_progress, status_callback=self.update_status, temperature=self.temperature, humidity=self.humidity)
            sf.write('processed.wav', processed_audio, sample_rate)
            self.update_status('Audio processed!')
        except Exception as e:
            self.update_status(f'Error processing audio!')
            print(e)

    def play_audio(self):
        try:
            self.update_status('Playing audio...')
            audio, sample_rate = sf.read('processed.wav')
            sd.play(audio, sample_rate)
            sd.wait()
            self.update_status('Audio played!')
        except Exception as e:
            self.update_status(f'Error playing audio: {e}')
            print(e)


class MainFrame(ttk.Frame):
    def __init__(self, container, shared_data):
        super().__init__(container)
        self.shared_data = shared_data
        self.base_parameters = BaseParameters(self, self.shared_data)
        self.mic_parameters = MicParameters(self, self.shared_data)
        self.src_parameters = SrcParameters(self, self.shared_data)
        self.file_frame = FileFrame(self, self.shared_data)
        self.calculations_parameters = CalculationsParameters(self, self.shared_data)
        self.base_parameters.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
        self.mic_parameters.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
        self.src_parameters.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)
        self.file_frame.grid(column=1, row=0, sticky=tk.W, padx=5, pady=5)
        self.calculations_parameters.grid(column=1, row=1, sticky=tk.W, padx=5, pady=5)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Room Impulse Response Generator")
        self.geometry("610x500")
        self.shared_data = SharedData()
        self.main_frame = MainFrame(self, self.shared_data)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def wait(self):
        self.wait_var = tk.StringVar()
        self.wait_var.set('wait')
        self.wait_window()

    def on_close(self):
        self.wait_var.set('closed')
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.wait()