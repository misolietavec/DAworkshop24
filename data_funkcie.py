import polars as pl
import plotly.express as px
import numpy as np

# Tu budeme pridavat funkcie pre spracovanie dat a kreslenie

df = pl.read_parquet('data/nyc_taxi310k.parq')
