import pickle
import polars as pl
import plotly.express as px
import numpy as np
import ipywidgets as ipw
from PIL import Image
from data_functions_sk import df, dfdays

meanloc = [df['pick_lat'].mean(), df['pick_lon'].mean()]


pick_images, drop_images = {}, {}
for hour in range(24):
    pick_images[hour] = Image.open(f'images/pick_{hour:02d}.jpg')
    drop_images[hour] = Image.open(f'images/drop_{hour:02d}.jpg')


def view_shaded(hour, direct):
    images = pick_images if (direct == 'Nástup') else drop_images
    return images[hour]


def play_hourly(value, direct):
    graf = dfdays[value]['pick_graph'] if direct == 'Nástup' else dfdays[value]['drop_graph']
    graf.update_layout(title='')
    graf.update_yaxes(range=[0, 750])  # odhad z grafov\n
    return graf


def view_hourly(day, direct):
    if direct == 'Nástup':
        return dfdays[day]['pick_graph']
    return dfdays[day]['drop_graph']


def df_for_map(day, hour, direct):
    pick_df = df.filter((pl.col('pick_day') == day) &
                        (pl.col('pick_hour') == hour)) 
    drop_df = df.filter((pl.col('drop_day') == day) &
                        (pl.col('drop_hour') == hour))
    data, what = (pick_df, 'pick') if direct == 'Nástup' else (drop_df, 'drop')
    return data, what

def view_distances(nb): 
    y, x = np.histogram(df['distance'], bins=nb, range=(0, 8))
    x = (x[0:-1] + x[1:]) / 2  # stredy intervalov
    df_hist = pl.DataFrame({'x': x, 'y': y}) # , 'zaokrúhlené': yr})
    return px.bar(data_frame=df_hist, x='x', y='y', #  'zaokrúhlené'], 
                  barmode='group', labels={'x': 'Vzdialenosť (km)', 'y': 'početnosť',
                                           'variable': 'hodnota'}, width=900, height=350)

def view_rtimes(nb):
    y, x = np.histogram(df['rtime'], bins=nb, range=(0, 45)) # min.
    x = (x[0:-1] + x[1:]) / 2  # stredy intervalov
    df_hist = pl.DataFrame({'x': x, 'y': y}) # , 'zaokrúhlené': yr})
    return px.bar(data_frame=df_hist, x='x', y='y', 
                  barmode='group', labels={'x': 'Čas jazdy (min.)', 'y': 'početnosť',
                                         'variable': 'hodnota'}, width=900, height=350)


def rides(day, hour, direct):
    data, what = df_for_map(day, hour, direct)
    return f"### Počet jázd: {data.shape[0]}"

