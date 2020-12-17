CONFLATE GTFS (Stop Segments) to LINE data (OSM, INRIX, etc...):
================================================================

12/04/2020:
===========
 - conflation (better ... matching) via PostGIS in Python
  - 1: broad query via st_ query(s):
    - run st_intersects(st_buffer(a.geom, 1.0), b.geom) to find tons of candidate matches 
    - maybe where clause this st_intersects data further (where highway, other st_ functions, etc...)
  - 2: find roads that match in direction and points in python
    - run https://postgis.net/docs/ST_LineInterpolatePoints.html and put this into 2 lists
    - run thru these points, looking to match a handful to determine where things overlap

  - questions
    - is there a pure postgis / st_ routine to find overlaps?
    - speed
    - how to test, etc?

  - queries
    - https://gis.stackexchange.com/questions/132259/postgis-conflation-of-two-vector-layers-into-a-single-layer
    - https://postgis.net/docs/ST_LineInterpolatePoints.html

SELECT --count(*)
a.id, b.xdsegid
--, st_length(ST_Intersection(ST_Buffer(a.geom, 1.005), b.geom)) as len
--, st_frechetdistance(a.geom, b.geom) as dist
--, st_hausdorffdistance(a.geom, b.geom) as dist
--, st_astext(ST_relate(a.geom, b.geom))
, ST_GeometryType(ST_Intersection(a.geom, b.geom))
, st_astext(ST_Intersection(a.geom, b.geom)) 
--, st_astext(ST_Intersection(st_buffer(a.geom, 0.5), b.geom)) 
--, st_astext(ST_SharedPaths(a.geom, b.geom))
---, st_length(st_makeline(ST_Intersection(a.geom, b.geom))), st_astext(st_makeline(ST_Intersection(a.geom, b.geom)))
FROM trimet.traffic_stop_segments a, trimet.traffic_inrix_segments b 
WHERE st_intersects(a.geom, b.geom) 
AND   st_contains(ST_Buffer(a.geom, 0.00001), b.geom)
--and not ST_IsEmpty(ST_Buffer(ST_Intersection(a.geom, b.geom), 1.0))
--and (st_length(ST_Intersection(st_buffer(a.geom, 1.0), b.geom)) > 0.010 )
limit 200


12/03/2020:
===========
can QGIS do queries, then view results? 

SELECT --count(*)
a.id, st_astext(st_makeline(ST_Intersection(a.geom, b.geom)))
FROM trimet.traffic_stop_segments a, trimet.traffic_inrix_segments b
WHERE st_intersects(a.geom, b.geom)
--and not ST_IsEmpty(ST_Buffer(ST_Intersection(a.geom, b.geom), 1.0));
and (st_length(st_makeline(ST_Intersection(st_buffer(a.geom, 1.0), b.geom))) > 0.010 )
group by a.id



11/17/2020:
===========
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