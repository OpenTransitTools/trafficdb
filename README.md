trafficdb
====
The Traffic Database aims to bring [GTFS](http://gtfs.org/reference/static), [OSM](https://www.openstreetmap.org/) and Traffic (Speed) data together. This project grew out of the US-FTA's 
[Integrated Mobility Innovation (IMI)](https://trimet.org/imi/about.htm) program. 


#### Example stop & traffic maps: 
- [TriMet (Portland, OR)](https://opentransittools.github.io/trafficdb/#11.0/45.51357/-122.66579/0/20) stop & traffic map
- [C-Tran (Vancouver, WA)](https://opentransittools.github.io/trafficdb?segments=ctran.geojson#11.0/45.582/-122.426/0/20) stop & traffic map 
- [ACTransit (Oakland, CA)](https://opentransittools.github.io/trafficdb?segments=actransit.geojson#11.0/37.6722/-122.0564/0/20) stop & traffic map 
- [RTD (Denver, CO)]() TBD


## Two options to install and run trafficdb (eventually) are either Docker Install or Manual Install

### Docker Install: todo

### Manual Install (step 1: mock data load):
- _prerequisite install_: git, postgres, psql, postgis, ogr2ogr, python 3.x, zc.buildout
- Clone the trafficdb repo: `git clone https://github.com/OpenTransitTools/trafficdb.git`
- `cd trafficdb`
- run the `scripts/create_db.sh` shell script
- run [buildout](https://pypi.org/project/zc.buildout/) to pull in python dependencies
- add your _INRIX credentials_ to config/base.ini
   - [inrix] 
    - vendorid = ___ 
    - consumerid = ___
    - note: if you don't do this, you won't see any speed data 
    - git update-index --assume-unchanged config/base.ini 
- run `bin/load_all -c -g -s test -d postgres://ott@localhost:5432/ott ott/trafficdb/model/inrix/test/gtfs.zip`
- run `bin/load_speed_data -s test -d postgres://ott@localhost:5432/ott`  # note: run this every N minutes to get up-to-date speed data into the database  

### Manual Install (real transit data load):
##### if the above load_all worked well, then the next step will be to load a full dataset
 - grab INRIX's .geojson traffic segment data from https://map-data-downloader.inrix.com/
   - for the example below, using TriMet's latest GTFS file, you should download and unzip the USA_Oregon_geojson.zip file 

https://developer.trimet.org/GTFS.shtml
bin/load_all -c -g -s test -d postgres://ott@localhost:5432/ott https://developer.trimet.org/schedule/gtfs.zip -t USA_Oregon.geojson
bin/load_speed_data -s trimet

https://www.c-tran.com/about-c-tran/business/c-tran-gtfs-data
bin/load_all -c -g -s ctran -d postgres://ott@localhost:5432/ott https://www.c-tran.com/images/Google/GoogleTransitUpload.zip -t USA_Washington.geojson USA_Oregon.geojson
bin/load_speed_data -s ctran

https://gtfs.vta.org/
bin/load_all -c -g -s vta -d postgres://ott@localhost:5432/ott https://gtfs.vta.org/gtfs_vta.zip -t USA_CA_BayArea.geojson 
bin/load_speed_data -s vta

http://www.actransit.org/planning-focus/data-resource-center/
bin/load_all -c -g -s actransit -d postgres://ott@localhost:5432/ott https://url.actransit.org/GtfsCurrent -t USA_CA_BayArea.geojson 
bin/load_speed_data -s actransit

https://www.rtd-denver.com/business-center/open-data/gtfs-developer-guide
note: problem with gtfsdb's GET and RTD's web server means that you probably need to download gtfs file locally and change the https: below to the file path of the downloaded .zip file  
bin/load_all -c -g -s rtd -d postgres://ott@localhost:5432/ott https://www.rtd-denver.com/files/gtfs/google_transit.zip -t USA_Colorado.geojson
bin/load_speed_data -s rtd


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
