import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.models import HoverTool, CustomJS, ColumnDataSource, Select
import datetime
import os

from bokeh.layouts import gridplot
from bokeh.resources import CDN
from bokeh.embed import file_html


def get_source(scores):
    source = ColumnDataSource(data=dict(
        x=scores['Points SFL'],
        y=scores["bet_safety"],
        team=scores["Equipe"],
        game=scores["Match"]
    ))
    return source


def main():
    files_list = os.listdir('data')

    scores_list = list()
    for file_path in files_list:
        scores = pd.read_csv('data/' + file_path)
        scores_list.append(scores)

    sources_list = list()
    for scores in scores_list:
        source = get_source(scores)
        sources_list.append(source)

    fill_source = get_source(scores_list[0])

    hover = HoverTool(
        tooltips=[
            ("Points", "@x"),
            ("Bet Safety", "@y"),
            ("Team", "@team"),
            ("Match", "@game")
        ],
        names=['teams']
    )

    output_file("index.html")

    p = figure(tools=[hover],
               title="SFL Data", y_axis_type="log")
    p.xaxis.axis_label = "Points SFL"
    p.yaxis.axis_label = "Bet Safety"

    p.scatter('x', 'y', radius=1, source=fill_source, name='teams', alpha=0.8)

    select = Select(options=files_list, value=files_list[0])

    codes = """
    var filename = cb_obj.value;
    var original_data = fill_source.data;
    var target_data = filename.data;

    console.log(target_data);

    original_data = target_data

    source.trigger("change");
    """

    source_dict = {k: v for k, v in zip(files_list, sources_list)}

    select.callback = CustomJS(args=dict(fill_source=fill_source, **source_dict), code=codes)

    grid = gridplot([[select], [p]])

    show(grid)


if __name__ == '__main__':
    main()

