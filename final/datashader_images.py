import polars as pl
import datashader as ds
from colorcet import fire
import datashader.transfer_functions as tf
import plotly.express as px

data_url = 'https://feelmath.eu/Download/nyc_taxi_rt.parq'
local_file = 'data/nyc_taxi_rt.parq'
df = pl.scan_parquet(local_file)
df = df.select(['pick_day', 'pick_hour', 'pick_lat', 'pick_lon',
                'drop_day', 'drop_hour', 'drop_lat', 'drop_lon']).collect()
c_lat, c_lon = [df['drop_lat'].mean(), df['drop_lon'].mean()]


def hours_data(df, hour, pick=True):
    h_col = 'pick_hour' if pick else 'drop_hour'
    lat, lon = ('pick_lat','pick_lon') if pick else ('drop_lat', 'drop_lon')
    h_frm = df.filter(pl.col(h_col) == hour)
    h_frm = h_frm.rename({lat: 'lat', lon: 'lon'}).select(['lat', 'lon'])
    return h_frm


def view_ds(hour, pick=True):
    frm = hours_data(df, hour, pick=pick)
    frm = frm.to_pandas()
    cvs = ds.Canvas(plot_width=1000, plot_height=710)
    agg = cvs.points(frm, x='lon', y='lat')
    cn_lat, cn_lon = agg.coords['lat'].values, agg.coords['lon'].values
    coordinates = [[cn_lon[0], cn_lat[0]], [cn_lon[-1], cn_lat[0]],
                   [cn_lon[-1], cn_lat[-1]], [cn_lon[0], cn_lat[-1]]]

    img = tf.shade(agg, cmap=fire)[::-1].to_pil()
    fig = px.scatter_mapbox(frm[:1], lat='lat', lon='lon', zoom=11, center={'lat': c_lat, 'lon': c_lon})
    fig.update_layout(#mapbox_style="open-street-map", 
                      mapbox_style='carto-darkmatter', height=710,
                     mapbox_layers = [
                    {
                        "sourcetype": "image",
                        "source": img,
                        "coordinates": coordinates,
                        "opacity": 0.9
                    }]
    )
    return fig


def write_images(pick=True):
    prefix = 'pick_' if pick else 'drop_'
    for hour in range(24):
        fig = view_ds(hour, pick)
        fig.write_image(f'images/{prefix}{hour:02d}.jpg')


# write_images()
# write_images(False)
