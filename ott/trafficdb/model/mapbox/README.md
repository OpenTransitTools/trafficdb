MAPBOX Traffic
===============

Price is about $50k per year for a state.  Talk to sales for more.
 - https://docs.mapbox.com/data/traffic/overview/example
 - https://blog.mapbox.com/traffic-data-supports-here-and-tomtom-with-real-time-and-historic-data-using-openlr-f6af26081a04

For my project, only interested in a sub-state region, so maybe $25k.
bbox=-123.12, 45.27, -122.36, 45.64

MB's data format is awesome for OSM users. Heistorical data is 1 week's data, at 5 minute intervals, for speeds between 2 OSM ways. 
nSo you see a (gzipped) .csv file for a region, with the following format:
 - NODE_1,NODE_2,speed_sunday_12am_MPH,..[2016 total speed measurements, ala every 5 minutes throughout the week]..,speed_saturday_11:55pm_MPH
 - NODE_3,NODE_4,speed_sunday_12am_MPH,..[2016 total speed measurements, ala every 5 minutes throughout the week]..,speed_saturday_11:55pm_MPH
 - etc...
 
Need to ingest the sample MapBox (MB) data and align it with OSM (maybe DT's OSM) data.
Map should show road segments for MB data.

Popup on each segment should have links to OSM, ala (these are actual nodes in the MB data):
  - https://www.openstreetmap.org/node/113163419
  - https://www.openstreetmap.org/node/113054533
  
Want to also show transit data underneath?
What else ... demongraphic data?

Does this system use a db? Or [pandas ala MB example](https://docs.mapbox.com/data/traffic/overview/example#calculate-aggregated-traffic-metrics)?

What about web services?  Needed? 
 - Give me speeds for transit route X (e.g., segments A-N)...caculate all segments making up this route
 - Or pattern K...caculate all segments making up pattern K
 - Service that just returns segment pair
 - Return a .csv file rathner than .json or .xml
 - Other stuff??  Route, Transit, Demograpics, ???
 

Sample Data:
 - Willmington NC has minimal GTFS data (just stops)
   can we order that limited data into ordered route stops 
   and thus into shapes
 - https://docs.mapbox.com/data/traffic/overview/example/
 - https://openmobilitydata.org/p/wave-transit/633/latest
 - http://tracking.wavetransit.com/
