import polars as pl
import plotly.express as px
import numpy as np

# Tu budeme pridavat funkcie pre spracovanie dat a kreslenie

# z NB 03_

df = pl.read_parquet('data/nyc_taxi310k.parq')

def monthly_frame(frm, day=True):      # nazvy stplcov v datafrejme mozu byt aj po slovensky :-)
    groupped = frm.group_by(pl.col('pick_dt').dt.day()) if day else\
               frm.group_by(pl.col('pick_dt').dt.hour())         
    column = 'pick_day' if day else 'pick_hour'
    df_month = groupped.agg([pl.col('fare').sum().alias('Platby'), 
                             pl.col('passengers').sum().alias('Cestujúci'),
                             pl.col('fare').count().alias('Jazdy')]).sort(by='pick_dt')
    df_month = df_month.rename({'pick_dt': column})   # pick_dt sa tu nehodi, bude pick_day alebo pick_hour
    return df_month


def monthly_plot(frm, day=True):
    mframe = monthly_frame(frm, day)
    xcol = 'pick_day' if day else 'pick_hour'
    xlabel = {'pick_day': 'Deň', 'pick_hour': 'Hodina'}
    xticks = {'pick_day': list(range(1, 32)), 'pick_hour': list(range(24))}
    pass_fares_plot = px.bar(mframe, x=xcol, y=['Cestujúci', 'Jazdy'], barmode='group',
                             labels={xcol: xlabel[xcol], 'value': 'Hodnoty', 'variable': 'Premenná'})
    pass_fares_plot.update_layout(xaxis=dict(tickmode='array', tickvals=xticks[xcol]))
    return pass_fares_plot


def week_plot(frm):
    df_weekday = (frm.group_by(pl.col('pick_dt').dt.weekday())
                     .agg(pl.col('passengers').count().alias('pass_count'))  # co keby sum namiesto count?
                     .sort(by='pick_dt'))
    df_weekday = df_weekday.rename({'pick_dt': 'pick_day'})
    pocty = np.array([4, 4, 4, 5, 5, 5, 4])  # preco nie len list?
    df_weekday = df_weekday.with_columns(pl.col('pass_count') / pocty)
    graf = px.bar(df_weekday, x='pick_day', y='pass_count', barmode='group', width=750, height=400)
    xtext = ['Pondelok', 'Utorok', 'Streda', 'Štvrtok', 'Piatok', 'Sobota', 'Nedeľa']
    graf.update_layout(xaxis=dict(tickmode='array', tickvals=list(range(1, 8)), title='Deň v týždni',
                       ticktext=xtext, tickangle=0), yaxis=dict(title="Priem. počet jázd"))
    return graf

# z NB 04_


def daily_frame(frm):   # vyvolame s df ako frm
    df_days = df.group_by(pl.col('pick_dt').dt.day().alias('pick_day'), 
                          pl.col('pick_dt').dt.hour().alias('pick_hour'))\
                         .agg([pl.col('passengers').sum().alias('pass_count'),
                               pl.col('fare').count().alias('fares_count'),
                               pl.col('fare').sum().alias('total_fare')])
    return df_days


def daily_plot(day): # frm tu bude povyssia df_days
    frm_d = daily_frame(df)
    frm_day = frm_d.filter(pl.col('pick_day') == day).sort(by='pick_hour')
    pass_fares_plot = px.bar(frm_day, x='pick_hour', y=['pass_count', 'fares_count'], barmode='group',
                             labels={'pick_hour': 'Hodina', 'value': 'Hodnoty', 'variable': 'Premenná'})
    pass_fares_plot.update_layout(xaxis=dict(tickmode='array', tickvals=list(range(24))))
    return pass_fares_plot


# z NB 05_

def dt_frame(frm): # frm bude povodna df
    df_dt = frm.with_columns(((pl.col('drop_dt') - pl.col('pick_dt')).cast(pl.Float32)/1000/60).alias('rtimes'))
    df_dt = df_dt.drop(['pick_dt', 'drop_dt'])
    return df_dt


def plot_histo(col, rozsah, nbins=20):
    xlabel = 'Vzdialenosť (míle)' if col == 'distance' else 'Čas jazdy'
    frm_dt = dt_frame(df)
    y, x = np.histogram(frm_dt[col], range=rozsah, bins=nbins)
    x = (x[0:-1] + x[1:]) / 2  # stredy intervalov, nie konce
    df_hist = pl.DataFrame({'x': x, 'y': y})  # pomocna frejma
    return px.bar(df_hist, x='x', y='y', barmode='group', 
                  labels={'x': xlabel, 'y': 'početnosť', 'variable': 'hodnota'}, width=900, height=350)

# z NB _06

def map_plot(frm, day, hour, pick=True):   # pick=False znamena, ze drop
    col_prefix = 'pick_' if pick else 'drop_'
    what = 'nástupy' if pick else 'výstupy'
    df_dh = frm.filter((pl.col(f'{col_prefix}dt').dt.day() == day) & (pl.col(f'{col_prefix}dt').dt.hour() == hour))
    mapa = px.scatter_mapbox(df_dh, lat=f'{col_prefix}lat', lon=f'{col_prefix}lon', mapbox_style="open-street-map", 
                         zoom=10, color_discrete_sequence=["darkblue"], width=500, height=500, opacity=0.3,
                         title=f'Počet jázd, {what}: {df_dh.shape[0]}')
    mapa.update_traces(marker={"size": 4})
    mapa.update_layout(margin={'t': 30, 'b': 10}, hovermode=False)
    return mapa

def pick_plot(day, hour):
    return map_plot(df, day, hour, pick=True)

def drop_plot(day, hour):
    return map_plot(df, day, hour, pick=False)
