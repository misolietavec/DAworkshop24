import polars as pl
import plotly.express as px

# Tu budeme pridavat funkcie pre spracovanie dat a kreslenie

# z 03 notebooku


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

