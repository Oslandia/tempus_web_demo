#!/bin/bash

set -u
set -e

echo "-----   INFO  ------"
echo "Insert several data into a PostgreSQL database"
echo "You need postgis, pgrouting, hstore, plpgsql and plpythonu extensions"
echo "see the 'database' ansible role in the dedicated ansible folder"
echo ""

if [ ! -f "config.ini" ]; then
    echo "ERROR: you need a 'config.ini' file"
    exit 0
fi

# load config.ini
dbname=$(grep -Po "(?<=dbname=).*" config.ini)
dbuser=$(grep -Po "(?<=dbuser=).*" config.ini)
schema=$(grep -Po "(?<=schema=).*" config.ini)
pgport=$(grep -Po "(?<=pgport=).*" config.ini)
srid=$(grep -Po "(?<=srid=).*" config.ini)

echo "#### Configuration variables"
echo "dbname: $dbname"
echo "dbuser: $dbuser"
echo "schema: $schema"
echo "pgport: $pgport"
echo "srid: $srid"
echo ""

echo "create the schema"
psql -p $pgport -U $dbuser -d $dbname -c "CREATE SCHEMA IF NOT EXISTS $schema;"

cmd="shp2pgsql -d -I"
intodb="psql -p $pgport -U $dbuser -d $dbname"
datadir="datarepo"

for fname in `cat shpdata.txt`; do
    if [ ! -f shapefiles/$fname.shp ]; then
        unzip -o "$datadir/$fname.zip" -d shapefiles
    fi
    IFS='.' read -ra NAME <<< "$fname"
    tbname=${NAME[1]}
    $cmd -s $srid shapefiles/$fname.shp $schema.$tbname | $intodb
done
