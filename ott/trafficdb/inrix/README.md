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
    - map data:
      - for things like the .geojson or .csv file of INRIX XD street segments
      - https://map-data-downloader.inrix.com
      - the INRIX sales rep authorized my uname to access the above url (it's my email address -- so this is a personal account)
      - INRIX's map-data-downloader site allows one to manually download their street data (geojson) ... 
        I grabbed data for Oregon & Washington (steps below) and loaded them into PostGIS...
      - data for other states & countries (and in other formats) is available here, plus a bit of documentation (schema, etc...)
      - run  this: ott/trafficdb/inrix/load_inrix_geojson.sh USA_*.geojson (and ignore any errors) to load INRIX streets / XD ids into PostGIS
      - view this: using QGIS (http://download.qgis.org/), and you should be able to see the INRIX data in PostGIS. see:
        ott/trafficdb/inrix/test/postgis_traffic_inrix_segments.qgz for a QGIS project that will view the
        INRIX street segment geojson data, which was loaded into postgis via load_inrix_geojson.sh
      
    - traffic api data:
      - this requires both a vendorid and consumerid 
      - one uses these two id's to then acquire an api token (which is valid for ~12 hours or so)
      - via the api token, you'll be able to call this api: http://docs.inrix.com/traffic/speed/
      - http://na.api.inrix.com/traffic/Inrix.ashx?format=json&action=getsecuritytoken
      - see: base.py / get_inrix_token(renew=False) function for more
 
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
   


