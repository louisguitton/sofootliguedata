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
    date_element = datetime.date.today().strftime("%Y%m%d")
    file_path = os.path.abspath('data/sfl_data_{}.csv'.format(date_element))
    scores = pd.read_csv(file_path)

    output_file(os.path.abspath("index.html"))

    source = get_source(scores)

    hover = HoverTool(
        tooltips=[
            ("Points", "@x"),
            ("Bet Safety", "@y"),
            ("Team", "@team"),
            ("Match", "@game")
        ],
        names=['teams']
    )

    p = figure(tools=[hover],
               title=file_path, y_axis_type="log")
    p.xaxis.axis_label = "Points SFL"
    p.yaxis.axis_label = "Bet Safety"

    p.scatter('x', 'y', radius=1, source=source, name='teams', alpha=0.8)

    show(p)

if __name__ == '__main__':
    main()

