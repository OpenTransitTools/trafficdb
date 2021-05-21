May 20, 2021 -- from discussion this morning w/init

To get trafficdb to do WMS, here's a short todo:
  1. look into Kartoza geoserver .. and getting it to talk to PostGIS
     - note couldn't get Kartoza's `docker pull kartoza/geoserver` talking with PostGIS running locally or running in another container (but didn't try hard .. networking)
     - maybe move to Kartoza docker-compose for PostGIS + GeoServer + ogr2ogr
     - https://github.com/kartoza/docker-geoserver/blob/master/docker-compose.yml
     - if we move, can we get all 3 to work?
 
   1. refactor speed load:
      - new table traffic_inrix_segment_speed to capture speeds for all inrix segments (e.g., traffic_segment table has FK's to transit shapes, so it won't be complete compared to entire INRIX data)
      - host 2 WMS / WFS layers .. show transit segment w/speed and also all segments with speed
      - maybe highlight traffic routes some way?
   
   1. What is the view for the WMS layer?  How to combine line geometry and speed data tables?
     - do we create a MVIEW of traffic_inrix_segments and traffic_inrix_segment_speed ?
     - do we create a GS layer using SQL w/in GeoServer?
       - https://docs.geoserver.geo-solutions.it/edu/en/adding_data/add_sqllayers.html
       - select * from trimet.traffic_segment_speed s, trimet.traffic_segment t where t.traffic_segment_id = s.traffic_segment_id
       - ...
     
   1. What about time data ... show speed now, and in recent past:
      - how to differentiate speed data in the database (now, 3 seconds ago, 6 seconds ago, et...)?
      - delete data after N seconds (separate thread? ... transaction locks)
     
   1. What other data do we bring in?
      - http://docs.inrix.com/traffic/dangerousslowdowns/
      - http://docs.inrix.com/traffic/xdincidents/
      - http://docs.inrix.com/traffic/trafficcameras/
  
