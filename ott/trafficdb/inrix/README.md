INRIX data ingestion steps:
===========================
 - system requirements:
   - bash / postgres / postgis / ogr2ogr / python 3.x + zc.buildout
   - this code runs in a *unix environment (both MacOS & CentOS tested)
   - the postgres database with postgis (geospatial extension) are required https://postgis.net/install/
   - bash shell scripting is used (pretty standard stuff in the *uinx world)
   - ogr2ogr is a tool to ingest geojson data from INRIX
   - python 3.x code is pretty core to the overall trafficdb project. 
     The INRIX specific python code is the stuff that both matches INRIX segment id data to TriMet transit segments
     Further, all the traffic / speed data that's pulled in from INRIX is done via python (plus setting up the database, etc...).

 - INRIX account access:
    - you will need 2 different authentication credentials
    - first is t 
 - INRIX data:
    - segment id data: 
      - there are per-state geojson (street geometry) files from INRIX, which map 
        out the
      - there is also a .csv file that maps INRIX Xd segment ids to OSM way ids
        (to date, I haven't found a use for that data) 

INRIX data:
===========

- The street geometry data for INRIX, has either INRIX id (xD id) to OSM way id (.csv file), or a street geometry file that has xD id data in the attribute / properties section.

To load geoson into a db:
 ogr2ogr -f "PostgreSQL" PG:"dbname=ott user=ott active_schema=trimet" -nln traffic_inrix_segments -overwrite ./test/inrix_small.geojsonl.json
   


