trafficdb
====
The Traffic Database aims to bring GTFS, OSM and Traffic (Speed) data together. This project grew out of the US-FTA's 
Integrated Mobility Innovation (IMI) program -- see https://trimet.org/imi/about.htm

#### Example map: https://opentransittools.github.io/trafficdb/#13.83/45.51357/-122.66579/0/20

## Two options to install and run trafficdb (eventually) are either Docker Install or Manual Install

### Docker Install: todo

### Manual Install (step 1: mock data load):
 - install: git, postgres, psql, postgis, ogr2ogr, python 3.x, zc.buildout
 - git clone https://github.com/OpenTransitTools/trafficdb.git
 - cd trafficdb
 - buildout
 - scripts/create_db.sh
 - add your inrix creds to config/base.ini
   - [inrix] 
    - vendorid = ___ consumerid = ___
    - note: if you don't do this, you won't see any speed data 
 - bin/load_all -c -g -s test -d postgres://ott@localhost:5432/ott ott/trafficdb/model/inrix/test/gtfs.zip
 - bin/load_speed_data -s test -d postgres://ott@localhost:5432/ott # note: run this every N minutes to get up-to-date speed data into the database 
 
### Manual Install (real data load):
##### if the above load_all worked well, then the next step will be to load a full dataset
 - grab INRIX's .geojson traffic segment data from https://map-data-downloader.inrix.com/
   - for the example below, using TriMet's latest GTFS file, you should download and unzip the USA_Oregon_geojson.zip file 
 - bin/load_all -c -g -s test -d postgres://ott@localhost:5432/ott https://developer.trimet.org/schedule/gtfs.zip -t USA_Oregon.geojson

### Individual Processes: CLEANUP TODO
 - step 1: load gtfs data ... calculate all stop-to-stop segments in the data 
   - bin/load_gtfs_data -c -g -s trimet -d postgres://ott@localhost/ott https://developer.trimet.org/schedule/gtfs.zip
 - step 2: load traffic vendor street / segment data (INRIX in this case)
   - ott/trafficdb/model/inrix/load_inrix_geojson.sh INRIX/USA_*.geojson
 - step 3: match/conflate stop-segments with traffic segment data
   - bin/match_segments
 - step 4: load speed data from INRIX into db (on-going ... run every 5 mintutes?)
   - bin/load_speed_data
 - step 5: plot lastest segment / speed data on the example map
   - bin/generate-speed-geojson --show-map

######  note: the load will take upwards of 1 hour (or more) ... but once done, you'll have a complete database with transit and speed data
 
## todo:
 - speed and osm data (example datasets) needed to complete things
 - create a docker container for the steps above!
 - create a second & third example around MapBox and/or TomTom data 
