trafficdb
====
The Traffic Database aims to bring [GTFS](http://gtfs.org/reference/static), [OSM](https://www.openstreetmap.org/) and Traffic (Speed) data together. This project grew out of the US-FTA's 
[Integrated Mobility Innovation (IMI)](https://trimet.org/imi/about.htm) program. 


#### Example stop & traffic maps: 
- [TriMet (Portland, OR)](https://opentransittools.github.io/trafficdb?segments=trimet.geojson#11.0/45.51357/-122.66579/0/20)
- [C-Tran (Vancouver, WA)](https://opentransittools.github.io/trafficdb?segments=ctran.geojson#11.0/45.582/-122.426/0/20)
- [RVTD (Medford, OR)](https://opentransittools.github.io/trafficdb?segments=rvtd.geojson#11.0/42.3121/-122.821/0/20)
- [ACTransit (Oakland, CA)](https://opentransittools.github.io/trafficdb?segments=actransit.geojson#11.0/37.6722/-122.0564/0/20)
- [VTA (San Jose, CA)](https://opentransittools.github.io/trafficdb?segments=vta.geojson#11.0/37.256/-121.8944/0/20)
- [RTD (Denver, CO)](https://opentransittools.github.io/trafficdb?segments=rtd.geojson#11.0/39.7036/-104.8601/0/20)
- [COTA (Columbus, OH)](https://opentransittools.github.io/trafficdb?segments=cota.geojson#11.0/39.9639/-82.9424/0/20)

### Manual Install 
- _prerequisite install_: git, postgres, psql, postgis, ogr2ogr (gdal), python 3.x, psycopg2-binary, zc.buildout.
  - note: there is a docker-compose alternative to installing PostGIS, gdal and ogr2ogr (see below)
  - for python, it should be just a matter of getting python installed, then doing a `pip install psycopg2-binary zc.buildout`
- clone the trafficdb repo: 
`git clone https://github.com/OpenTransitTools/trafficdb.git`
- `cd trafficdb`
- run the `scripts/db/create.sh` shell script
- run [buildout](https://pypi.org/project/zc.buildout/) to pull in python dependencies
- add your _INRIX credentials_ to *trafficdb/config/base.ini*
   - [inrix] 
    - vendorid = ___ 
    - consumerid = ___
    - note: if you don't do this, you won't see any speed data 
    - git update-index --assume-unchanged config/base.ini 
- run `bin/load_all -c -g -s test -d postgres://ott@localhost:5432/ott ott/trafficdb/model/inrix/test/gtfs.zip`
- run `bin/load_speed_data -s test -d postgres://ott@localhost:5432/ott`  # note: run this every N minutes to get up-to-date speed data into the database  

### Docker-Compose alternative install of PostGIS and GDAL:
- install Docker and Docker-Compose 
- cd transitdb
- docker-compose up
- . ./scripts/docker_dot_source_me.sh


### Manual Install (real transit data load):
##### if the above load_all worked well, then the next step will be to load a full dataset
 - grab INRIX's .geojson traffic segment data from https://map-data-downloader.inrix.com/
   - for the example below, using TriMet's latest GTFS file, you should download and unzip the USA_Oregon_geojson.zip file 

https://developer.trimet.org/GTFS.shtml
bin/load_all -c -g -s trimet -t $PWD/USA_Oregon.geojson -d postgres://ott@localhost:5432/ott https://developer.trimet.org/schedule/gtfs.zip
bin/load_speed_data -s trimet

https://www.rvtd.org/Page.asp?NavID=60
bin/load_all -c -g -s rvtd -t $PWD/USA_Oregon.geojson -d postgres://ott@localhost:5432/ott http://feed.rvtd.org/googleFeeds/static/google_transit.zip
bin/load_speed_data -s rvtd

https://www.c-tran.com/about-c-tran/business/c-tran-gtfs-data
bin/load_all -c -g -s ctran -t $PWD/USA_Washington.geojson $PWD/USA_Oregon.geojson -d postgres://ott@localhost:5432/ott https://www.c-tran.com/images/Google/GoogleTransitUpload.zip
bin/load_speed_data -s ctran

https://gtfs.vta.org/
bin/load_all -c -g -s vta -t $PWD/USA_CA_BayArea.geojson -d postgres://ott@localhost:5432/ott https://gtfs.vta.org/gtfs_vta.zip
bin/load_speed_data -s vta

http://www.actransit.org/planning-focus/data-resource-center/
bin/load_all -c -g -s actransit -t $PWD/USA_CA_BayArea.geojson -d postgres://ott@localhost:5432/ott https://url.actransit.org/GtfsCurrent
bin/load_speed_data -s actransit

https://www.rtd-denver.com/business-center/open-data/gtfs-developer-guide
curl https://www.rtd-denver.com/files/gtfs/google_transit.zip > x  # note: gtfsdb's current HTTP GET routine doesn't work with RTD's server / redirects 
bin/load_all -c -g -s rtd -t $PWD/USA_Colorado.geojson -d postgres://ott@localhost:5432/ott x
bin/load_speed_data -s rtd

https://www.cota.com/data/
bin/load_all -c -g -s cota -t $PWD/USA_Ohio.geojson -d postgres://ott@localhost:5432/ott https://www.cota.com/COTA/media/COTAContent/OpenGTFSData.zip
bin/load_speed_data -s cota


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
