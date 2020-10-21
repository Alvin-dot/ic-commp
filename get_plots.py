from bokeh.plotting import figure, output_file, show
from bokeh.models import HoverTool, Range1d
from bokeh.models.tickers import AdaptiveTicker
from bokeh.layouts import column


def plot_config(plot_title, x_axis_label, y_axis_label, x_axis_data, y_axis_data, x_axis_type='auto',
                x_min=None, x_max=None):
    """
    Configures a plot using the Bokeh module
    Returns the plot class
    -------------
    plot_title: string, plot title
    x_axis_label: string, x axis label
    y_axis_label: string, y axis label
    x_axis_data: list, x axis data
    y_axis_data: list, y axis data
    x_axis_type: string, optional, selects the type of data on x axis (mainly used as 'datetime' for frequency)
    x_min: int, optional, sets minimum x axis value
    x_max: int, optional, sets maximum x axis value
    """

    signal_dict = {x_axis_label: x_axis_data, y_axis_label: y_axis_data}

    # Creates the hover tooltip
    tt = HoverTool(tooltips=[
        (x_axis_label, f"@{{{x_axis_label}}}"),
        (y_axis_label, f"@{{{y_axis_label}}}")
    ])

    # Plot main configuration
    signal_plot = figure(title=plot_title,
                         x_axis_label=x_axis_label,
                         y_axis_label=y_axis_label,
                         plot_width=1200,
                         plot_height=600,
                         x_axis_type=x_axis_type,
                         tools=[tt, 'wheel_zoom', 'pan', 'reset'])
    # Line drawing for the plot
    signal_plot.line(x_axis_label, y_axis_label, line_width=2, source=signal_dict, alpha=0.8)
    # Sets the number of ticks in the y axis
    signal_plot.yaxis.ticker = AdaptiveTicker(desired_num_ticks=10)
    # Sets the title text font size
    signal_plot.title.text_font_size = '16pt'
    # Sets the axis text font style
    signal_plot.axis.axis_label_text_font_style = 'bold'

    # Sets x axis scale based on user input
    if x_min or x_max:
        signal_plot.x_range = Range1d(x_min, x_max)

    return signal_plot


def show_plots(*args, file_name='results.html'):
    # Sets the output file name and extention
    output_file(file_name)
    # Plots the graphs in a column
    show(column(*args))
