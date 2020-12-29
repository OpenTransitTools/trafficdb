trafficdb
====
The Traffic database aims to bring GTFS, OSM and Traffic (Speed) data together. This project grew out of the US-FTA's 
Integrated Mobility Innovation (IMI) -- see https://trimet.org/imi/about.htm

### See: https://opentransittools.github.io/trafficdb/#13.83/45.51357/-122.66579/0/20

### Steps:
 - install: git, postgres, postgis, python 3.x, zc.buildout
 - git clone https://github.com/OpenTransitTools/trafficdb.git
 - cd trafficdb
 - buildout
 - scripts/create_db.sh
 - bin/load_all -c -g -s ttt -d postgres://ott@localhost:5432/ott ott/trafficdb/model/inrix/test/gtfs.zip
 
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

######  note:  the load will take upwards of 1 hour (or more) ... but once done, you'll have a complete database with transit and speed data
 
## todo:
 - speed and osm data (example datasets) needed to complete things
 - create a docker container for the steps above!
 - create a second & third example around MapBox and/or TomTom data 
