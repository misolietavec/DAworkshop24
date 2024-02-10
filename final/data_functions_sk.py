import polars as pl
import plotly.express as px
import os, pickle
import numpy as np

dfdays = pickle.load(open('data/dfdays.pic','rb'))
df = pl.read_parquet('data/nyc_taxi155k.parq')


def get_totals(frm, pick=True):
    columns = [pl.col('pick_day'), pl.col('pick_hour')] if pick else [pl.col('drop_day'), pl.col('drop_hour')]
    df_total = frm.group_by(columns)\
                            .agg([pl.col('fare').sum().alias('Platby'),\
                                  pl.col('passengers').sum().alias('Cestujúci'),
                                  pl.col('fare').count().alias('Jazdy')])\
                            .sort(by=columns)
    return df_total

    
def total_graphs(frm, pick=True, height=400, width=750, what=['Cestujúci', 'Jazdy', 'Platby'], 
                 monthly=False, day=True):
    if not monthly:
        frm = get_totals(frm) if pick else get_totals(frm, pick=False)
        column = 'pick_hour' if pick else 'drop_hour'
    else: 
        column = ('pick_day' if pick else 'drop_day') if day else ('pick_hour' if pick else 'drop_hour')
    ylabel = 'Nástupy' if pick else 'Výstupy'
    max_jaz, max_pas, max_far = frm['Jazdy'].max(), frm['Cestujúci'].max(), frm['Platby'].max()
    coeff = max(max_jaz, max_pas) / max_far
    trzba = frm['Platby'].sum()
    frm = frm.with_columns(pl.col('Platby') * coeff)
    scalestr = f"Platby vynásobené {coeff:.3f}, skutočné platby {trzba:.2f}" if ('Platby' in what) else ''
    colname = 'Hodina' if not (monthly and day) else 'Deň' 
    graf = px.bar(frm, x=column, y=what, barmode='group', height=height, width=750, title=scalestr, 
                  labels={column: colname, 'variable': 'Premenná', 'value': 'Hodnota'})
    if monthly and day:
        xtext = 4 * ['Štv', 'Pi', 'So', 'Ne', 'Po', 'Ut', 'Str'] + ['Štv', 'Pi', 'So']
        xtext = [f"{ind + 1}, {dni}" for ind, dni in enumerate(xtext)]
        graf.update_layout(xaxis=dict(tickmode='array', tickvals=list(range(1, 32)),
                           ticktext=xtext, tickangle=70), yaxis=dict(title=ylabel))
    else:
        graf.update_layout(xaxis=dict(tickmode='array', tickvals=list(range(24))), yaxis=dict(title=ylabel))  
    return graf


# We will make plots only once, then load them from pickle file
def make_graphs(df, create=True):
    plotfile = 'data/dfdays.pic'
    if create:
        dfdays = {}
        for day in range(1, 32):
            pick_df = df.filter(pl.col('pick_day') == day) 
            drop_df = df.filter(pl.col('drop_day') == day)
            dfdays[day] = {}
            dfdays[day]['pick_graph'] = total_graphs(pick_df) 
            dfdays[day]['drop_graph'] = total_graphs(drop_df, pick=False)
        pickle.dump(dfdays, open(plotfile,'wb'))
    else:
        dfdays = pickle.load(open(plotfile,'rb'))
    return dfdays


def monthly_frame(frm, pick=True, day=True):
    column = ('pick_day' if pick else 'drop_day') if day else ('pick_hour' if pick else 'drop_hour')
    df_month = frm.group_by(column).agg([pl.col('fare').sum().alias('Platby'), 
                                         pl.col('passengers').sum().alias('Cestujúci'),
                                         pl.col('fare').count().alias('Jazdy')]).sort(by=column)
    return df_month

def weekday_plot(frm):
    df_wd = frm.with_columns(pl.date(2015, 1, pl.col('pick_day')).dt.weekday().alias('wday'))\
                           .select(['pick_day', 'wday'])
    wdcount = np.array([4, 4, 4, 5, 5, 5, 4])
    wstat = df_wd.group_by(pl.col('wday')).agg(pl.col('wday').count().alias('counts')).sort(by='wday')
    wstat = wstat.with_columns(pl.col('counts') / wdcount)  # aby bolo na jeden den v tyzdni, inak nespravodlivo
    graf = px.bar(wstat, x='wday', y='counts', barmode='group', orientation='v', width=750, height=400)
    xtext = ['Pondelok', 'Utorok', 'Streda', 'Štvrtok', 'Piatok', 'Sobota', 'Nedeľa']
    graf.update_layout(xaxis=dict(tickmode='array', tickvals=list(range(1, 8)), title='Deň v týždni',
                       ticktext=xtext, tickangle=0), yaxis=dict(title="Priem. počet jázd"))
    return graf


# Plots - pickups and dropoffs by hour (rides, passenger count, fare), total
def static_graphs(frm):
    pick_days = total_graphs(monthly_frame(frm), height=350, width=900, monthly=True)
    drop_days = total_graphs(monthly_frame(frm, pick=False), height=350, width=900, monthly=True, pick=False)
    pick_hours = total_graphs(monthly_frame(frm, day=False), height=350, width=900, monthly=True, day=False)
    drop_hours = total_graphs(monthly_frame(frm, pick=False, day=False), height=350, width=900, 
                              monthly=True, pick=False, day=False) 
    return pick_days, drop_days, pick_hours, drop_hours


pick_days, drop_days, pick_hours, drop_hours = static_graphs(df)
weekdays = weekday_plot(df)


