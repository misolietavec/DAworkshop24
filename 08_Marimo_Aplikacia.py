import marimo

__generated_with = "0.2.13"
app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def _():
    from final.data_funkcie import pick_plot, drop_plot, view_month_week, week_plot, daily_plot, histo_dists, histo_times
    return (
        daily_plot,
        drop_plot,
        histo_dists,
        histo_times,
        pick_plot,
        view_month_week,
        week_plot,
    )


@app.cell
def _(mo):
    # widgety, graficke prvky
    day_choose = mo.ui.slider(start=1, stop=31, value=14, label='Deň', debounce=True)
    hour_choose = mo.ui.slider(start=0, stop=23, value=11, label='Hodina', debounce=True)
    direction = mo.ui.radio(options=['Nástup', 'Výstup'], value='Nástup', inline=True)
    # pre mesacne grafy
    day_hour_choose = mo.ui.radio(options=['Podľa dní', 'Podľa hodín', 'Dni v týždni (nástupy)'], 
                                  value= 'Podľa dní', inline=True)
    # pre histogramy
    nbins_choose = mo.ui.slider(start=10, stop=120, value=20, label='Počet tried', debounce=True)
    # percentily pre histogramy, nove
    quant_choose = mo.ui.slider(start=5, stop=95, step=5, value=50, label='Percentil', debounce=True)
    return (
        day_choose,
        day_hour_choose,
        direction,
        hour_choose,
        nbins_choose,
        quant_choose,
    )


@app.cell
def _(day_hour_choose, mo, view_month_week):
    tab_monthly = mo.vstack([day_hour_choose, view_month_week(day_hour_choose.value)])
    return tab_monthly,


@app.cell
def _(day_choose, drop_plot, hour_choose, mo, pick_plot):
    tab_map = mo.vstack([mo.hstack([day_choose, hour_choose], justify='start'), 
                         mo.hstack([pick_plot(day_choose.value, hour_choose.value), 
                                    drop_plot(day_choose.value, hour_choose.value)])])
    return tab_map,


@app.cell
def _(daily_plot, day_choose, mo):
    tab_daily = mo.vstack([day_choose, daily_plot(day_choose.value)])
    return tab_daily,


@app.cell
def _(histo_dists, histo_times, mo, nbins_choose, quant_choose):
    tab_histo = mo.vstack([mo.hstack([nbins_choose, quant_choose], justify='start'), 
                           histo_dists(nbins_choose.value, quant_choose.value), 
                           histo_times(nbins_choose.value, quant_choose.value)])
    return tab_histo,


@app.cell
def _(mo, tab_daily, tab_histo, tab_map, tab_monthly):
    tabs = mo.ui.tabs({'Grafy mesačné': tab_monthly, 'Miesta na mape': tab_map, 
                       'Grafy po dňoch': tab_daily, "Histogramy": tab_histo})
    return tabs,


@app.cell
def _(mo):
    nadpis = mo.md(
        """
        # Taxi v New Yorku
        ### Dáta z januára 2015, vzorka 310000 zápisov, celkovo je ich vyše 11 mil.
        """)
    return nadpis,


@app.cell
def _(mo, nadpis, tabs):
    app = mo.vstack([nadpis, tabs])
    app
    return app,


if __name__ == "__main__":
    app.run()
