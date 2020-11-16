GTFS to OSM
===========

raw data:
 - trip id => shape id => multiple points forming a line
 - OSM Node A, OSM Node B, week's worth of speeds at 5 min intervals
 
link datasets:
 - trip id => shape id (points) <=LINK=> line between OSM Node A & B
 - 
  
pattern id => OSM road segments => segment speeds

/q: 
 - trip id ... return pattern with segmented speeds