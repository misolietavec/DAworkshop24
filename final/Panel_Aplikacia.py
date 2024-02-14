import panel as pn
import panel.widgets as pnw
from final.data_funkcie import pick_plot, drop_plot, view_month_week, daily_plot, histo_dists, histo_times 
pn.extension('plotly', 'ipywidgets')

# widgety, graficke prvky
day_choose = pnw.IntSlider(start=1, end=31, value=14, width=250, name='Deň')
hour_choose = pnw.IntSlider(start=0, end=23, value=11, width=300, name='Hodina')
direction = pnw.RadioBoxGroup(options=['Nástup','Výstup'], inline=True)
day_hour_choose = pnw.RadioBoxGroup(options=['Podľa dní','Podľa hodín', 'Dni v týždni (nástupy)'], inline=True)
nbins_choose = pnw.IntSlider(start=10, end=120, value=20, width=250, name='Počet tried')

bind_monthly = pn.bind(view_month_week, doh=day_hour_choose)
tab_monthly = pn.Column(day_hour_choose, bind_monthly)

bind_pick = pn.bind(pick_plot, day=day_choose, hour=hour_choose)
bind_drop = pn.bind(drop_plot, day=day_choose, hour=hour_choose)
tab_map = pn.Column(pn.Row(day_choose, hour_choose), pn.Row(bind_pick, bind_drop))

bind_daily = pn.bind(daily_plot, day=day_choose)
tab_daily = pn.Column(day_choose, bind_daily)

bind_dists = pn.bind(histo_dists, bins=nbins_choose)
bind_times = pn.bind(histo_times, bins=nbins_choose)
tab_histo = pn.Column(nbins_choose, bind_dists, bind_times)

tabs = pn.Tabs(('Grafy mesačné', tab_monthly), ('Miesta na mape', tab_map), 
               ('Grafy po dňoch', tab_daily), ("Histogramy", tab_histo), dynamic=True) 

nadpis = pn.pane.Markdown(
    """
    # Taxi v New Yorku
    ### Dáta z januára 2015, vzorka 310000 zápisov, celkovo je ich vyše 11 mil.
    """)

app = pn.Column(nadpis, tabs).servable()
