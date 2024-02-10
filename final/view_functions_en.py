import marimo as mo
from data_functions_en import total_graphs
import pickle
import numpy as np
import polars as pl
import plotly.express as px

dfdays = pickle.load(open('data/dfdays_en.pic','rb'))

def _view_hourly(dc, dir):
    if dir == 'Pickup':
        return dfdays[dc]['pick_graph']
    return dfdays[dc]['drop_graph']

def _view_distances(df, bins): 
    y, x = np.histogram(df['distance'], bins=bins, range=(0, 8))
    x = (x[0:-1] + x[1:]) / 2
    df_hist = pl.DataFrame({'x': x, 'y': y})
    return px.bar(data_frame=df_hist, x='x', y='y', 
                  barmode='group', labels={'x': 'Distance', 'y': 'count'}, width=900, height=350)


def _view_rtimes(df, bins):
    y, x = np.histogram(df['rtime'], bins=bins, range=(0, 45)) # min.
    x = (x[0:-1] + x[1:]) / 2  # centers of intervals
    df_hist = pl.DataFrame({'x': x, 'y': y})
    return px.bar(data_frame=df_hist, x='x', y='y', 
                  barmode='group', labels={'x': 'Ride time (min.)', 'y': 'count'}, width=900, height=350)


def _view_map(df, dir, dcv, hcv):
    is_pick = (dir == 'Pickup')
    col_day = 'pick_day' if is_pick else 'drop_day'
    col_hour = 'pick_hour' if is_pick else 'drop_hour'
    df_filtered = df.filter((df[col_day] == dcv) & (df[col_hour] == hcv))
    col_lat = 'pick_lat' if is_pick else 'drop_lat'
    col_lon = 'pick_lon' if is_pick else 'drop_lon'
    lat, lon = df_filtered[col_lat], df_filtered[col_lon]
    center_lat, center_lon = [lat.mean(), lon.mean()] if len(lat) else meanloc
    fig = px.scatter_mapbox(df_filtered, lat=col_lat, lon=col_lon,
                            color_discrete_sequence=["green"],
                            mapbox_style="open-street-map", zoom=10, width=750, height=500)
    fig.update_traces(marker={"size": 4})
    fig.update_layout(margin={'t': 25}, hovermode=False)
    return mo.ui.plotly(fig)


def _view_selection(df, mapplot, selval, mdv):
    _local_data = ((mapplot.ranges != {}) and selval)
    if _local_data:
        mapranges = mapplot.ranges['mapbox']
        lon_min, lat_max = mapranges[0]
        lon_max, lat_min = mapranges[1]
        df_ranges_pick = df.filter((lat_min < pl.col('pick_lat')) & (pl.col('pick_lat') < lat_max) &
                                   (lon_min < pl.col('pick_lon')) & (pl.col('pick_lon') < lon_max) &
                                   (pl.col('pick_day') == mdv))
        df_ranges_drop = df.filter((lat_min < pl.col('drop_lat')) & (pl.col('drop_lat') < lat_max) &
                                   (lon_min < pl.col('drop_lon')) & (pl.col('drop_lon') < lon_max) &
                                   (pl.col('drop_day') == mdv))
        pick_rows = (df_ranges_pick.rows() != [])
        drop_rows = (df_ranges_drop.rows() != [])
        no_rides = mo.md("## No rides here")
        pick_plot = total_graphs(df_ranges_pick, pick=True, height=350) if pick_rows else no_rides
        drop_plot = total_graphs(df_ranges_drop, pick=False, height=350) if drop_rows else no_rides
    else: 
        no_plot = mo.md('## No selection, or selection not enabled')
        return no_plot
    return mo.vstack([pick_plot, drop_plot])

