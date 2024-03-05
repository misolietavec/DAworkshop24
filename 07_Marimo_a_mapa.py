import marimo

__generated_with = "0.2.13"
app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __():
    from final.data_funkcie import pick_plot, drop_plot
    return drop_plot, pick_plot


@app.cell
def __(mo):
    day_choose = mo.ui.slider(start=1, stop=31, value=14, label='Deň')
    hour_choose = mo.ui.slider(start=0, stop=23, value=11, label='Hodina')
    return day_choose, hour_choose


@app.cell
def __(day_choose, drop_plot, hour_choose, mo, pick_plot):
    mo.vstack([mo.hstack([day_choose, hour_choose]), 
               mo.hstack([pick_plot(day_choose.value, hour_choose.value), 
                          drop_plot(day_choose.value, hour_choose.value)])])
    return


if __name__ == "__main__":
    app.run()
