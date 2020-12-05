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
    - map data from https://map-data-downloader.inrix.com:
      - INRIX's map-data-downloader site allows one to manually download their street data (geojson)
        (e.g., I grabbed data for Oregon & Washington, and loaded them into PostGIS... see steps below).
      - the INRIX sales rep authorized my uname to access the above url (e.g., is email address -- thus a personal account)
      - the map-data-downloader site contains data for other states & countries, in a variety of formats (.csv, .json, .shp, etc...)
      - **run  this:** ott/trafficdb/inrix/load_inrix_geojson.sh USA_*.geojson (and ignore any errors) to load INRIX streets / XD ids into PostGIS
      - **view this:** using QGIS (http://download.qgis.org/), and you should be able to see the INRIX data in PostGIS.
        _ott/trafficdb/inrix/test/postgis_traffic_inrix_segments.qgz_ is a QGIS project file that should connect to your 
        local PostGIS db, and show the INRIX street segment geojson data that was loaded into postgis via load_inrix_geojson.sh (above)

    - traffic api data:
      - this requires both an INRIX 'vendorid' and 'consumerid' 
      - these two id credentials are then used to acquire an api token (which is valid for ~12 hours or so)
      - the api token will then allow calls to INRIX's traffic api: http://docs.inrix.com/traffic/speed/
      - http://na.api.inrix.com/traffic/Inrix.ashx?format=json&action=getsecuritytoken&vendorid=__your_vid__&consumerid=__your_cid__
      - see function get_inrix_token(renew=False) in base.py, for code that programmatically acquires an INRIX api token
 