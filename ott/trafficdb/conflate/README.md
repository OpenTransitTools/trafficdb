GTFS to OSM
===========

11/17/2020:
 - find nodes / ways along a trip / pattern / shape:
   - minimal is 2 stops (and not geom data)
   - maximal has shapes data + 2 stops ... that shape data should intersect closely with some OSM way(s)
   - OSM might have multiple ways / nodes along the way and/or between 2 stops
   - distill that data down to what ???:
     - for inrix data, would be nodes from stops/OSM ... and then find ways that match those nodes
     - for mapbox data, it would be OSM nodes ... which you'd then be looking to match

 Questions:
  - Is correct?: a "start_stop, end_stop" transit segment always travels along the same street(s) / same path?
  - Could there be a condition where tripX,stopA,stopB travels differently than tripY,stopA,stopB?  (ask Myleen)


thoughts:
 - "a segment as the path between two bus stops that exists in at least one line and pattern in the transportation system" (from the TransLink paper)
 - trip stops: show stops along a trip, indexed via shape (shape and stop times per trip are same, right ... coudl be different?)
 - what is the time / speed (avg) between 2 stops along a trip
 - need to relate trip / shapes / osm sections to one another...
 - (research why speed is important in the model ... how is speed cut up and applied to the model)
 - is stop to stop the proper speed interpolation?  sub-divide stop to stop (where it can be done)
 - ...


raw data:
 - trip id => shape id => multiple points forming a line
 - OSM Node A, OSM Node B, week's worth of speeds at 5 min intervals
 
link datasets:
 - trip id => shape id (points) <=LINK=> line between OSM Node A & B
 - 
  
pattern id => OSM road segments => segment speeds

/q: 
 - trip id ... return pattern with segmented speeds