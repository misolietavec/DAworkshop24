import marimo

__generated_with = "0.1.88"
app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __():
    import polars as pl
    from data_functions_sk import static_graphs
    from view_functions_sk import _view_hourly, _view_distances, _view_rtimes, _view_map, _view_selection
    return pl, static_graphs


@app.cell
def __(pl):
    nsample = 155000
    _dflocal = 'data/nyc_taxi155k.parq'
    df = pl.read_parquet(_dflocal)
    meanloc = [df['pick_lat'].mean(), df['pick_lon'].mean()]
    return df, meanloc, nsample


@app.cell
def __(df, mo, static_graphs):
    _pick_days, _drop_days, _pick_hours, _drop_hours = static_graphs(df)
    static_days = mo.vstack([_pick_days, _drop_days])
    static_hours = mo.vstack([_pick_hours, _drop_hours])
    return static_days, static_hours


@app.cell
def __(mo):
    day_choose = mo.ui.slider(start=1, stop=31, value=14, debounce=True, label='Deň')
    hour_choose = mo.ui.slider(start=0, stop=23, value=11, debounce=True, label='Hodina')
    direction = mo.ui.radio(options=['Nástup','Výstup'], value='Nástup', label='Smer', inline=True)
    map_selection = mo.ui.checkbox(label='Umožniť výber')
    day_or_hour = mo.ui.radio(options=['Podľa dní','Podľa hodín'], value='Podľa dní', inline=True)
    nbins = mo.ui.slider(start=10, stop=120, value=20, debounce=True, label='Počet tried')
    return (
        day_choose,
        day_or_hour,
        direction,
        hour_choose,
        map_selection,
        nbins,
    )


@app.cell
def __(day_choose, mo):
    map_day_choose = mo.ui.slider(start=1, stop=31, value=day_choose.value, debounce=True, label='Deň pre výber')
    return map_day_choose,


@app.cell
def __(day_choose, direction, mo):
    _hourly_info = mo.md(f"Deň: {day_choose.value}")
    hourly = mo.vstack([mo.hstack([direction, day_choose, _hourly_info], justify='center'), 
                        _view_hourly(day_choose.value, direction.value)], align='center')
    return hourly,


@app.cell
def __(df, mo, nbins):
    dist_and_times = mo.vstack([mo.hstack([nbins, mo.md(f"Poč. tried: {nbins.value}")], justify='center'),
                                _view_distances(df, nbins.value), _view_rtimes(df, nbins.value)])
    return dist_and_times,


@app.cell
def __(day_or_hour, mo, static_days, static_hours):
    def _view_totals():
        return static_days if day_or_hour.value == 'Podľa dní' else static_hours
    totals = mo.vstack([day_or_hour, _view_totals()], align='center')
    return totals,


@app.cell
def __(day_choose, df, direction, hour_choose):
    mapplot = _view_map(df, direction.value, day_choose.value, hour_choose.value)
    return mapplot,


@app.cell
def __(
    day_choose,
    df,
    direction,
    dist_and_times,
    hour_choose,
    hourly,
    map_day_choose,
    map_selection,
    mapplot,
    mo,
    nsample,
    totals,
):
    _main_title = mo.md(
        f"""
        # Taxi v New Yorku
        ### Dáta z januára 2015, výber {nsample} záznamov.""")

    _local_data =(mapplot.ranges != {}) and map_selection.value
    _local_plots = _view_selection(df, mapplot, map_selection.value, map_day_choose.value)
    _sel_info = mo.md(f"Deň: {map_day_choose.value}")
    _loc_widgets = mo.hstack([map_day_choose, _sel_info], justify='center', widths=[100, 50])
    _selection_body = mo.vstack([_loc_widgets, _local_plots]) if _local_data else mo.vstack([_local_plots])

    _map_info = mo.md(f"Deň: {day_choose.value}, Hodina: {hour_choose.value}")
    _maps = mo.vstack([mo.hstack([direction, day_choose, hour_choose, map_selection], justify='center'), 
                      _map_info, mapplot], align='center')
    _tabs = mo.tabs({'Grafy po dňoch': hourly, 'Grafy celkové': totals, 'Histogramy': dist_and_times,
                     'Polohy na mape': _maps, 'Grafy pre výber': _selection_body})

    app_tabs = mo.vstack([_main_title, _tabs], align='stretch') 
    app_tabs
    return app_tabs,


if __name__ == "__main__":
    app.run()
