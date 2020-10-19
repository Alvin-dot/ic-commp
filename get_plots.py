import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.models import HoverTool
from bokeh.models.tickers import AdaptiveTicker
from bokeh.layouts import column


def plot_config(plot_title, x_axis_label, y_axis_label, x_axis_data, y_axis_data):
    signal_df = pd.DataFrame({x_axis_label: x_axis_data,
                              y_axis_label: y_axis_data})

    tt = HoverTool(tooltips=[
        (x_axis_label, f"@{{{x_axis_label}}}"),
        (y_axis_label, f"@{{{y_axis_label}}}")
    ])

    signal_plot = figure(title=plot_title,
                         x_axis_label=x_axis_label,
                         y_axis_label=y_axis_label,
                         plot_width=1200,
                         plot_height=600,
                         tools=[tt, 'wheel_zoom', 'pan', 'reset'])
    signal_plot.line(x_axis_label, y_axis_label, line_width=2, source=signal_df, alpha=0.8)
    signal_plot.yaxis.ticker = AdaptiveTicker(desired_num_ticks=10)
    signal_plot.title.text_font_size = '16pt'
    signal_plot.axis.axis_label_text_font_style = 'bold'

    return signal_plot


def show_plots(*args, file_name='results.html'):
    output_file(file_name)
    show(column(*args))
