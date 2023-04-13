import numpy as np
from bokeh.palettes import Turbo256 as tol
from bokeh.plotting import figure, show
from bokeh.models import Slider, CustomJS, ColumnDataSource
from bokeh.layouts import column
from functions_ import calculate_responses, compute_rir

room_dim = (5, 4, 3)
abs = 0.5
mic_positions = {
    "mic_1": (2.5, 2, 1),
    "mic_2": (2.5, 2.5, 1),
    "mic_3": (2.5, 3, 1)
}
src_positions = {
    "src_1": (1, 1, 1.5),
    "src_2": (3, 1, 1.5),
    "src_3": (2, 1, 1.5)
}


def main():
    abs = 0.5
    room = compute_rir(room_dim, absorption=abs, max_order=3, mic_positions=mic_positions, src_positions=src_positions)
    freq_responses = calculate_responses(room, mic_positions, src_positions, norm=True, freqresp=True) 

    p = figure(title="Frequency response of the room impulse response", 
               x_axis_label="Frequency [Hz]", 
               y_axis_label="Amplitude [dB]")
    for mic_idx, (freq, response) in freq_responses.items():
        p.line(
            freq, 
            y=20 * np.log10(np.abs(response)),
            color=tol[np.random.randint(0, 256)], 
            legend_label=mic_idx
            )
    p.legend.location = "top_left"
    p.legend.click_policy="hide"
    p.background_fill_color = "whitesmoke"
    p.grid.grid_line_color = "white"
    
    #create callback to update the plot when the slider value changes, 
    callback = CustomJS(args=dict(p=p), code="""
            var data = abs.value;
            var f = cb_obj.value;
            data = f;
            source.change.emit();
    """)
    slider = Slider(start=0, end=1, value=0.5, step=0.1, title="Absorption coefficient")
    slider.js_on_change('value', callback)
    show(column(p, slider))



if __name__ == "__main__":
    main()



# potential room designer tool: PolyDrawTool