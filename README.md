## Data analysis workshop for beginners (PyCon SK 2024)

We will use `NYC taxi dataset`, data from January, 2015. This is modified
dataset from https://s3.amazonaws.com/datashader-data/nyc_taxi_wide.parq
used in `holoviz` ecosystem https://holoviz.org/. Column names are shortened. 
For workshop we will need only the sample of 310000 records
(`data/nyc_taxi_sample.parq`). Full modified dataset is available at https://feelmath.eu/Download/nyc_taxi.parq.

For running the notebooks, modules `panel, ipyleaflet,
polars, pandas, pyarrow, fastparquet, plotly` need to be installed. 

Docker image with all workshop files can be pulled by
`docker pull misolietavec/daworkshop`. The `Dockerfile` in this directory is
for creating such (or similar) images. Running with 

`docker run -p 3500:8888 misolietavec/daworkshop` 

will give you Jupyterlab application at `http://127.0.0.1:3500/lab`.
