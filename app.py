from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import fastf1
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib import cm
import numpy as np
import io
import base64


import plotly.tools as pt


df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

session = fastf1.get_session(2021, 'Spanish Grand Prix', 'Q')
session.load()

drivers = pd.unique(session.laps['Driver'])
app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Formula one Visualizing', style={'textAlign':'center'}),
    dcc.Dropdown(drivers, drivers[0], id='driver-1-dd'),
    dcc.Dropdown(drivers, drivers[0], id='driver-2-dd'),
    # dcc.Graph(id='driver-1'),
    # dcc.Graph(id='driver-2')

    html.Img(id="driver-1"),
    html.Img(id="driver-2"),

])

def get_data_for_plotting(lap,wheretosave):
    tel = lap.get_telemetry()
    x = np.array(tel['X'].values)
    y = np.array(tel['Y'].values)

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    gear = tel['nGear'].to_numpy().astype(float)

    cmap = cm.get_cmap('Paired')
    lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N + 1), cmap=cmap)
    lc_comp.set_array(gear)
    lc_comp.set_linewidth(4)

    plt.gca().add_collection(lc_comp)
    plt.axis('equal')
    plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

    title = plt.suptitle(
        f"Fastest Lap Gear Shift Visualization\n"
        f"{lap['Driver']} - {session.event['EventName']} {session.event.year}"
    )

    cbar = plt.colorbar(mappable=lc_comp, label="Gear", boundaries=np.arange(1, 10))
    cbar.set_ticks(np.arange(1.5, 9.5))
    cbar.set_ticklabels(np.arange(1, 9))

    # f= plt.figure()
    # pt.tools.mpl_to_plotly(f)
    # plt.savefig(f"./assets/{wheretosave}.png")
    # plt.cla()
    # plt.clf()
    buf = io.BytesIO()  # in-memory files
    plt.scatter(x, y)
    plt.savefig(buf, format="png")
    plt.close()
    data = base64.b64encode(buf.getbuffer()).decode("utf8")  # encode to html elements
    buf.close()
    return "data:image/png;base64,{}".format(data)

@callback(
    Output('driver-1', 'src'),
    Output('driver-2', 'src'),
    Input('driver-1-dd', 'value'),
    Input('driver-2-dd', 'value')

)
def update_graph(driver1,driver2):
    session1 = fastf1.get_session(2021, 'Spanish Grand Prix', 'Q')
    session1.load()

    session2 = fastf1.get_session(2021, 'Spanish Grand Prix', 'Q')
    session2.load()
    lapL = session1.laps.pick_driver(driver1).pick_fastest()
    lapR = session2.laps.pick_driver(driver2).pick_fastest()

    left=get_data_for_plotting(lapL,"lapL")
    right=get_data_for_plotting(lapR, "lapR")
    return left,right




if __name__ == '__main__':
    app.run_server(debug=True)