import marimo as mo
import numpy as np
import polars as pl
import plotly.express as px


def daily_frame(frm, pick=True):   # vyvolame s df ako frm
    col_prefix='pick_' if pick else 'drop_'
    df_days = frm.group_by(pl.col(f'{col_prefix}dt').dt.day().alias(f'{col_prefix}day'), 
                           pl.col(f'{col_prefix}dt').dt.hour().alias(f'{col_prefix}hour'))\
                          .agg([pl.col('passengers').sum().alias('pass_count'),
                                pl.col('fare').count().alias('fares_count'),
                                pl.col('fare').sum().alias('total_fare')])
    return df_days


def _daily_plot(frm, day, pick=True): # frm tu bude povyssia df_days, day bude z radio day_choose
    frm_d = daily_frame(frm, pick=pick)
    col_prefix='pick_' if pick else 'drop_'
    val_label = 'Nástupy' if pick else 'Výstupy'
    frm_day = frm_d.filter(pl.col(f'{col_prefix}day') == day).sort(by=f'{col_prefix}hour')
    pass_fares_plot = px.bar(frm_day, x=f'{col_prefix}hour', y=['pass_count', 'fares_count'], barmode='group', height=350,
                             labels={f'{col_prefix}hour': 'Hodina', 'value': val_label, 'variable': 'Premenná'})
    pass_fares_plot.update_layout(xaxis=dict(tickmode='array', tickvals=list(range(24))))
    return pass_fares_plot


def _view_map(df, dir, dcv, hcv):
    is_pick = (dir == 'Nástup')
    column = 'pick_dt' if is_pick else 'drop_dt'
    df_filtered = df.filter((df[column].dt.day() == dcv) & (df[column].dt.hour() == hcv))
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
                                   (pl.col('pick_dt').dt.day() == mdv))
        df_ranges_drop = df.filter((lat_min < pl.col('drop_lat')) & (pl.col('drop_lat') < lat_max) &
                                   (lon_min < pl.col('drop_lon')) & (pl.col('drop_lon') < lon_max) &
                                   (pl.col('drop_dt').dt.day() == mdv))
        pick_rows = (df_ranges_pick.rows() != [])
        drop_rows = (df_ranges_drop.rows() != [])
        no_rides = mo.md("## Nikto nejazdil")
        pick_plot = _daily_plot(df_ranges_pick, mdv, pick=True) if pick_rows else no_rides
        drop_plot = _daily_plot(df_ranges_drop, mdv, pick=False) if drop_rows else no_rides
    else: 
        no_plot = mo.md('## Źiadny výber, alebo výber nie je povolený')
        return no_plot
    return mo.vstack([pick_plot, drop_plot])