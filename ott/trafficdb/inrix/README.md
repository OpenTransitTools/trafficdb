INRIX data:
===========

The street geometry data for INRIX, has either INRIX id (xD id) to OSM way id (.csv file), or a street geometry file that has xD id data in the attribute / properties section.

To load geoson into a db:
 ogr2ogr -f "PostgreSQL" PG:"dbname=ott user=ott active_schema=trimet" -nln traffic_inrix_segments -overwrite ./test/inrix_small.geojsonl.json
   


