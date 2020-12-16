TOMTOM Traffic
===============

Don't know too mmuch about their data (Dec 2020), but worth checking out in the future.
They do offer a 'free' tier to access their data (e.g. free allows 2500 transactions per-day).
https://developer.tomtom.com/store/maps-api

##TRAFFIC SPEEDS

https://developer.tomtom.com/traffic-api/traffic-api-documentation-traffic-flow/flow-segment-data#response-data


##TRAFFIC DENSITY

https://developer.tomtom.com/content/traffic-api-explorer

##### DESCRIPTION:

One dataset that TOMTOM offers (i.e., saw this on the CARTO site) is historic traffic volume (e.g., number of
vehicles on a road segment), broken out by the day/hour, as well as a daily average.

##### FORMAT:

The data has columns for sun, mon, tue..., which represent the average number of vehicles per hour for the given day.
Additionally, there's a sun_1, sun_2 ... sun_23, mon_1 ... mon_23, tue_1 ... etc... that shows the number of
vehicles on that road segment during that hour of that given day.  
 
##### SEE
  - test/tomtom_traffic_desnisty.geojson for some example data.
