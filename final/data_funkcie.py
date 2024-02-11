import polars as pl
import plotly.express as px
import numpy as np

# Tu budeme pridavat funkcie pre spracovanie dat a kreslenie

# z NB 03_


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


def daily_plot(frm, day): # frm tu bude povyssia df_days
    frm_day = frm.filter(pl.col('pick_day') == day).sort(by='pick_hour')
    pass_fares_plot = px.bar(frm_day, x='pick_hour', y=['pass_count', 'fares_count'], barmode='group',
                             labels={'pick_hour': 'Hodina', 'value': 'Hodnoty', 'variable': 'Premenná'})
    pass_fares_plot.update_layout(xaxis=dict(tickmode='array', tickvals=list(range(24))))
    return pass_fares_plot


# z NB 05_

def dt_frame(frm): # frm bude povodna df
    df_dt = frm.with_columns(((pl.col('drop_dt') - pl.col('pick_dt')).cast(pl.Float32)/1000/60).alias('rtimes'))
    df_dt = df_dt.drop(['pick_dt', 'drop_dt'])
    return df_dt


def plot_histo(frm, col, rozsah, nbins=20):
    xlabel = 'Vzdialenosť (míle)' if col == 'distance' else 'Čas jazdy'
    y, x = np.histogram(frm[col], range=rozsah, bins=nbins)
    x = (x[0:-1] + x[1:]) / 2  # stredy intervalov, nie konce
    df_hist = pl.DataFrame({'x': x, 'y': y})  # pomocna frejma
    return px.bar(df_hist, x='x', y='y', barmode='group', 
                  labels={'x': xlabel, 'y': 'početnosť', 'variable': 'hodnota'}, width=900, height=350)