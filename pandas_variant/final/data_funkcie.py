import pandas as pd
import plotly.express as px
import numpy as np

# Zakladna frejma, vsetko pochadza z nej
df = pd.read_parquet('data/nyc_taxi310k.parq')
df['pick_day'] = df['pick_dt'].dt.day
df['pick_hour'] = df['pick_dt'].dt.hour

# Tu budeme pridavat funkcie pre spracovanie dat a kreslenie

# z NB 03_


def monthly_frame(frm, day=True):      # nazvy stplcov v datafrejme mozu byt aj po slovensky :-)
    groupped = frm.groupby(frm['pick_dt'].dt.day) if day else\
               frm.groupby(frm['pick_dt'].dt.hour)         
    column = 'pick_day' if day else 'pick_hour'
    df_month = pd.DataFrame(groupped['passengers'].sum().astype('float32')).rename(columns={'passengers': 'Cestujúci'})
    df_month['Platby'] = groupped['fare'].sum() 
    df_month['Jazdy'] = groupped['fare'].count()
    df_month[column] = df_month.index
    return df_month

# V aplikacii budeme mat radiobox s volbami ['Podľa dní','Podľa hodín', 'Dni v týždni (nástupy)']

def monthly_plot(dhc):
    day = (dhc == 'Podľa dní')
    xcol = 'pick_day' if day else 'pick_hour'
    mframe = monthly_frame(df, day)
    xcol = 'pick_day' if day else 'pick_hour'
    xlabel = {'pick_day': 'Deň', 'pick_hour': 'Hodina'}
    xticks = {'pick_day': list(range(1, 32)), 'pick_hour': list(range(24))}
    pass_fares_plot = px.bar(mframe, x=xcol, y=['Cestujúci', 'Jazdy'], barmode='group',
                             labels={xcol: xlabel[xcol], 'value': 'Hodnoty', 'variable': 'Premenná'})
    pass_fares_plot.update_layout(xaxis=dict(tickmode='array', tickvals=xticks[xcol]))
    return pass_fares_plot


def week_plot(frm):
    groupped = frm.groupby(frm['pick_dt'].dt.weekday)
    df_weekday = pd.DataFrame(groupped['passengers'].count())
    df_weekday['pick_day'] = df_weekday.index + 1
    df_weekday = df_weekday.rename(columns={'passengers': 'pass_count'})                    
    pocty = np.array([4, 4, 4, 5, 5, 5, 4])
    print(df_weekday.columns)
    df_weekday['pass_count'] = df_weekday['pass_count'] / pocty
    graf = px.bar(df_weekday, x='pick_day', y='pass_count', barmode='group', width=750, height=400)
    xtext = ['Pondelok', 'Utorok', 'Streda', 'Štvrtok', 'Piatok', 'Sobota', 'Nedeľa']
    graf.update_layout(xaxis=dict(tickmode='array', tickvals=list(range(1, 8)), title='Deň v týždni',
                       ticktext=xtext, tickangle=0), yaxis=dict(title="Priem. počet cestujúcich"))
    return graf

# v aplikacii budu tie tri grafy - mesacne podla hodin, dni a tyzdenny v jednej 'zalozke'

def view_month_week(doh):
    if doh in ['Podľa dní', 'Podľa hodín']:
        return monthly_plot(doh)
    return week_plot(df)

# z NB 04_

def daily_frame(frm):   # vyvolame s df ako frm
    groupped = df.groupby(['pick_day', 'pick_hour'])
    df_days = groupped['passengers'].aggregate("sum").reset_index()
    df_days = df_days.rename(columns={'passengers': 'pass_count'})
    df_days['fares_count'] = groupped['fare'].count().reset_index()['fare']
    df_days['total_fare'] = groupped['fare'].sum().reset_index()['fare']
    return df_days


def daily_plot(day): # frm tu bude povyssia df_days
    frm_d = daily_frame(df)
    frm_day = frm_d[frm_d['pick_day'] == day].sort_values(by='pick_hour')
    pass_fares_plot = px.bar(frm_day, x='pick_hour', y=['pass_count', 'fares_count'], barmode='group',
                             labels={'pick_hour': 'Hodina', 'value': 'Hodnoty', 'variable': 'Premenná'})
    pass_fares_plot.update_layout(xaxis=dict(tickmode='array', tickvals=list(range(24))))
    return pass_fares_plot

# z NB 05_

def plot_histo(col, rozsah, nbins=20, quant=50):
    xlabel = 'Vzdialenosť (míle)' if col == 'distance' else 'Čas jazdy'
    y, x = np.histogram(df[col], range=rozsah, bins=nbins)
    x = (x[0:-1] + x[1:]) / 2  # stredy intervalov, nie konce
    df_hist = pd.DataFrame({'x': x, 'y': y})  # pomocna frejma
    rt_plot = px.bar(df_hist, x='x', y='y', barmode='group', 
                     labels={'x': xlabel, 'y': 'početnosť', 'variable': 'hodnota'}, width=900, height=350)
    rt_plot.add_vline(df[col].quantile(quant / 100), line={'color':'red'})
    return rt_plot

def histo_dists(bins, quant):
    return plot_histo('distance', (0, 8), bins, quant)

def histo_times(bins, quant):
    return plot_histo('rtime', (0, 35), bins, quant)


# z NB _06

def map_plot(frm, day, hour, pick=True):   # pick=False znamena, ze drop
    col_prefix = 'pick_' if pick else 'drop_'
    what = 'nástupy' if pick else 'výstupy'
    df_dh = frm[(frm[f'{col_prefix}dt'].dt.day == day) & (frm[f'{col_prefix}dt'].dt.hour == hour)]
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
