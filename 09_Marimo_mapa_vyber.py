import marimo

__generated_with = "0.2.13"
app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __():
    import polars as pl
    from final.view_functions import _view_map, _view_selection
    return pl,


@app.cell
def __(pl):
    df = pl.read_parquet('data/nyc_taxi310k.parq')
    meanloc = [df['pick_lat'].mean(), df['pick_lon'].mean()]
    return df, meanloc


@app.cell
def __(mo):
    day_choose = mo.ui.slider(start=1, stop=31, value=14, debounce=True, label='Deň')
    hour_choose = mo.ui.slider(start=0, stop=23, value=11, debounce=True, label='Hodina')
    direction = mo.ui.radio(options=['Nástup','Výstup'], value='Nástup', label='Smer', inline=True)
    map_selection = mo.ui.checkbox(label='Umožniť výber')
    map_day_choose = mo.ui.slider(start=1, stop=31, value=14, debounce=True, label='Deň pre výber')
    return day_choose, direction, hour_choose, map_day_choose, map_selection


@app.cell
def __(day_choose, df, direction, hour_choose):
    mapplot = _view_map(df, direction.value, day_choose.value, hour_choose.value)
    return mapplot,


@app.cell
def __(
    day_choose,
    df,
    direction,
    hour_choose,
    map_day_choose,
    map_selection,
    mapplot,
    mo,
):
    _main_title = mo.md(
        """
        # Taxi v New Yorku
        ### Dáta z januára 2015, výber 310000 záznamov.""")

    _local_data =(mapplot.ranges != {}) and map_selection.value
    _local_plots = _view_selection(df, mapplot, map_selection.value, map_day_choose.value)
    _sel_info = mo.md(f"Deň: {map_day_choose.value}")
    _loc_widgets = mo.hstack([map_day_choose, _sel_info], justify='center', widths=[100, 50])
    _selection_body = mo.vstack([_loc_widgets, _local_plots]) if _local_data else mo.vstack([_local_plots])

    _map_info = mo.md(f"Deň: {day_choose.value}, Hodina: {hour_choose.value}")
    _maps = mo.vstack([mo.hstack([direction, day_choose, hour_choose, map_selection], justify='center'), 
                      _map_info, mapplot], align='center')
    _tabs = mo.ui.tabs({'Polohy na mape': _maps, 'Grafy pre výber': _selection_body})

    app_tabs = mo.vstack([_main_title, _tabs], align='stretch') 
    app_tabs
    return app_tabs,


if __name__ == "__main__":
    app.run()
