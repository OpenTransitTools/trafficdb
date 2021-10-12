CONFLATE GTFS (Stop Segments) to LINE data (OSM, INRIX, etc...):
================================================================

The current INRIX to GTFS conflation routines need work.  In the readme below is a running diary of differnt thoughts and ideas on both what was tried, and also how this work may be improved in the future.


10/13/2020:
===========

https://gis.stackexchange.com/questions/349001/aligning-line-with-closest-line-segment-in-postgis

This is a classic road network conflation problem. It has the following challenges:
- determining a set of matched road segments to a path line in spite of them being very different lengths
- clipping the matched road segments to the path line (this is best done after merging the matched road segments (the "path lines" are the red lines in the diagram)

For the matching, a sketch of an approach is:
- For each path line, select the road segments which are within a distance tolerance d
- For each matched road segment, "clip" the path line to it (clipping explained below)
- Discard any clipped segments which have length 0 (these are segments which are roughly perpendicular to the path, e.g. cross streets)
- Compute the Hausdorff distance between the road segment and the clipped path, and keep only segments with a distance below the tolerance d (this discards road segments where only one end is near the path)
- Clip each road segment to the path line (to discard pieces of the road segment which extend beyond the path)
- Merge the clipped road segments together

Other apps:
https://github.com/ad-freiburg/pfaedle - stop to stop matched to OSM for a detailed line

1/3/2020:
===========

Anything here?  https://github.com/mapsme/osm_conflate/tree/master/conflate

-- select count(distinct shape_id) from trimet.traffic_stop_segment_trips
--DROP TABLE ctran.traffic_stop_segments_t;
--CREATE TABLE ctran.traffic_stop_segments_t AS SELECT * FROM ctran.traffic_stop_segments;
--ALTER TABLE ctran.traffic_stop_segments_t ALTER COLUMN geom TYPE GEOMETRY(POLYGON, 4326) USING ST_Buffer(geom, 0.001);
--CREATE INDEX idx_traffic_stop_segments_t_geom ON ctran.traffic_stop_segments_t USING gist (geom);

SELECT --count(*)
a.id, b.id, a.direction, b.direction
---, ST_Contains(a.geom, b.geom) as a_cont_b_exact -- always false
, ST_Contains(st_buffer(a.geom, 0.00001), b.geom) as a_cont_b_sm
, ST_Contains(st_buffer(a.geom, 0.0001), b.geom) as a_cont_b_md
, ST_Contains(st_buffer(a.geom, 0.001), b.geom) as a_cont_b_lg
, (select c.shape_pt_sequence from test.shapes c where ST_Equals(ST_ClosestPoint(ST_Points(a.geom), st_startpoint(b.geom)), c.geom) and a.shape_id = c.shape_id limit 15) as start 
, (select c.shape_pt_sequence from test.shapes c where ST_Equals(ST_ClosestPoint(ST_Points(a.geom), st_endpoint(b.geom)), c.geom) and a.shape_id = c.shape_id limit 15) as endd
, ST_AsText(ST_ClosestPoint(ST_Points(a.geom), st_startpoint(b.geom))) as close_start
, ST_AsText(ST_ClosestPoint(ST_Points(a.geom), st_endpoint(b.geom))) as close_end

--, (select c.shape_pt_sequence from ctran.shapes c where ST_Equals(ST_ClosestPoint(c.geom, st_startpoint(b.geom)), c.geom) and a.shape_id = c.shape_id limit 1) as start 
--, (select c.shape_pt_sequence from ctran.shapes c where ST_Equals(ST_ClosestPoint(c.geom, st_endpoint(b.geom)), c.geom) and a.shape_id = c.shape_id limit 1) as endd

--, (select c.shape_id from ctran.shapes c where a.shape_id = c.shape_id and ST_ClosestPoint(st_startpoint(b.geom), c.ge
om)) limit 1)
--, ST_AsText(ST_ClosestPoint(ST_Points(a.geom), st_endpoint(b.geom)))
--, (select ST_AsText(ST_ClosestPoint(c.geom, st_endpoint(b.geom))) from ctran.shapes c where a.shape_id = c.shape_id li
mit 1)
--, (select ST_AsText(ST_ClosestPoint(c.geom, st_endpoint(b.geom))) from ctran.shapes c where a.shape_id = c.shape_id li
mit 1)
--, ST_Distance(a.geom, st_endpoint(b.geom))
--, (select ST_Distance(ST_ClosestPoint(c.geom, st_endpoint(b.geom)), st_endpoint(b.geom)) from ctran.shapes c where a.s
hape_id = c.shape_id limit 1)
--, (select ST_Distance(c.geom, st_endpoint(b.geom)) from ctran.shapes c where a.shape_id = c.shape_id limit 1)
--, (select c.shape_pt_sequence from ctran.shapes c where a.shape_id = c.shape_id limit 1)
, a.*
, b.*
FROM test.traffic_stop_segments a, test.traffic_inrix_segments b
WHERE 
--st_intersects(a.geom, b.geom)
--st_intersects(st_buffer(a.geom, 0.001), b.geom)
st_dwithin(a.geom, b.geom, 0.001)
--and a.id = '2706-3242'
--and a.shape_id = '5332'
--and a.shape_id = '462934'
--and start < end
--and ST_Contains(st_buffer(a.geom, 0.0001), b.geom)
--and start != NULL
--and end != NULL
--and start < endd
order by start
--limit 600



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
