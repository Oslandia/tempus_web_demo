# Data Used for the Demo

We used several open data from the French city Lyon which it's
called [Data Grand Lyon](https://data.grandlyon.com/).

There can be a restricted access for some data (real time traffic, public
transport). Please sign up to get these data.

## Download Data

We use the [luigi](https://github.com/spotify/luigi) Python library to get all
available open data. We use the Data Grand Lyon WFS service to get all
geospatial data in a shapefile format. By default, the Python script `tasks.py`
downloads the shapefiles with the projection WGS 84 (SRID: 4326).

You have to install `luigi`. Then, launch the script `luigi.sh` to get all data
into the folder `datarepo`. There are less than 200 zip files. Sometimes, you
will see a 401 error. There are some limited access resources which ask an
authorization. We have decided to ignore these data for now.

