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
 - bin/load-gtfs-and-speed-data -c -g -s tm -d postgres://localhost/ott https://developer.trimet.org/schedule/gtfs.zip
 
 note the load will take upwards of 1 hour ... but once done, you'll have a complete database with speed data
 
## Todo:
 - speed and osm data (example datasets) needed to complete things
 - create a docker container for the steps above!
 - create a second (first) example around MapBox data 
