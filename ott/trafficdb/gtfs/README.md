GTFS to OSM
===========

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