import marimo

__generated_with = "0.2.2"
app = marimo.App(width="full")


@app.cell
def _():
    import polars as pl
    from final.data_funkcie import df, pick_plot, drop_plot, monthly_plot, week_plot, daily_plot, plot_histo
    return (
        daily_plot,
        df,
        drop_plot,
        monthly_plot,
        pick_plot,
        pl,
        plot_histo,
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
    return day_choose, day_hour_choose, direction, hour_choose, nbins_choose


@app.cell
def _(day_hour_choose, df, mo, monthly_plot, week_plot):
    def _view_monthly(dhc):
        if  dhc == 'Podľa dní':
            return monthly_plot(df, day=True)
        elif dhc == 'Podľa hodín':
            return monthly_plot(df, day=False)
        else:
            return week_plot(df)

    tab_monthly = mo.vstack([day_hour_choose, _view_monthly(day_hour_choose.value)])
    return tab_monthly,


@app.cell
def _(day_choose, drop_plot, hour_choose, mo, pick_plot):
    tab_map = mo.vstack([mo.hstack([day_choose, hour_choose]), 
                        mo.hstack([pick_plot(day_choose.value, hour_choose.value), 
                                   drop_plot(day_choose.value, hour_choose.value)])])
    return tab_map,


@app.cell
def _(daily_plot, day_choose, mo):
    tab_daily = mo.vstack([day_choose, daily_plot(day_choose.value)])
    return tab_daily,


@app.cell
def _(mo, nbins_choose, plot_histo):
    def _histo_dists(bins):
        return plot_histo('distance', (0, 8), bins)
    def _histo_times(bins):
        return plot_histo('rtimes', (0, 35), bins)

    tab_histo = mo.vstack([nbins_choose, _histo_dists(nbins_choose.value), 
                              _histo_times(nbins_choose.value)])
    return tab_histo,


@app.cell
def _(mo, tab_daily, tab_histo, tab_map, tab_monthly):
    tabs = mo.tabs({'Grafy mesačné': tab_monthly, 'Miesta na mape': tab_map, 
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


@app.cell
def _():
    import marimo as mo
    return mo,


if __name__ == "__main__":
    app.run()
