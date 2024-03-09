FROM python:3.11-slim

LABEL maintainer Michal Kaukic <mike@feelmath.eu>
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-utils curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y --no-install-recommends tini nodejs procps \
    && pip install -U pip \
    && pip install polars fastparquet plotly marimo notebook \
       ipywidgets_bokeh pyarrow panel ipyleaflet jupyterhub==4.0.2 \
       jupyter-server-proxy jupyter_bokeh==2.0.4 \
    &&  adduser --home /home/jovyan --shell /bin/bash --uid 1000 --gid 100 \
    --disabled-password --quiet jovyan \
    && mkdir /home/jovyan/notebooks && mkdir /home/jovyan/.jupyter \
    && rm /bin/sh && ln -s /bin/bash /bin/sh \
    && apt-get autoremove -y && apt-get clean \
    && rm -fr /root/.cache/pip/* /var/lib/apt/lists/*  /usr/local/share/.cache \
    && rm /bin/chmod && rm -fr /tmp/* \
    && rm -fr /root/.npm \
    && rm /etc/localtime \
    && ln -s /usr/share/zoneinfo/Europe/Bratislava /etc/localtime \
    && echo "Europe/Bratislava" > /etc/timezone \
    && rm /bin/sh \ 
    && ln -s /bin/bash /bin/sh

EXPOSE 8888
WORKDIR /home/jovyan/notebooks

# Configure container startup
ENTRYPOINT ["tini", "--"]
CMD ["jupyter", "lab", "--no-browser", "--NotebookApp.token=''", "--ip=0.0.0.0"]

RUN chown -R jovyan:users /home/jovyan

USER jovyan
COPY --chown=jovyan:jovyan dawork /home/jovyan/notebooks
