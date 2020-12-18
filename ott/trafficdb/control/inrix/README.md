About INRIX Data
=====


##Speed Data

##### Speeds
 - 'reference': 19 -- The free flow speed on the segment for the given day and time 
 - 'average': 19 -- The typical speed on the segment for the given day and time 
 - 'speed': 26 -- Current speed on the segment 
 - 'travelTimeMinutes': 0.243
 - segmentClosed: boolean (e.g., there won't be speed data above if segment is closed)
 - see: http://docs.inrix.com/traffic/speed/#get-getsegmentspeed
 - subsegment speeds:

##### Confidence:
 - 'score': 30 (real-time data) and 'c-Value': 0-100 (% confidence)
 - 'score': 20 (mix of historic and real-time) and 'c-Value': ??? (not sure there is a value here)
 - 'score': 10 (historic data .. no probes) and 'c-Value': ??? (not sure there is a value here)
 - see: https://lib.dr.iastate.edu/cgi/viewcontent.cgi?article=1196&context=creativecomponents
 
 
 ## Incident Data

https://na-api.inrix.com/Traffic/Inrix.ashx?action=GetXDIncidentsInBox&units=0&locale=en-US&corner1=45.427913|-122.810884&corner2=45.447878|-122.750244&incidentSource=INRIXonly&incidentType=Incidents&geometryTolerance=10&incidentoutputfields=all&locrefmethod=XD&token=XyuTFaOVwZXMfPYFIWj2Gcvmhw427QW7J-gvdHNC*AA|&compress=true&format=json

 
`
{"docType":"GetXDIncidentsInBox","copyright":"Copyright INRIX Inc.","versionNumber":"17.3","createdDate":"2020-12-18T02:50:57Z","statusId":0,"statusText":"OK","responseId":"212ccd83-dfb9-42e6-beda-df1c66d97148","result":{"XDIncidents":[{"id":138963676,"version":"4","type":"4","severity":"2","geometry":{"type":"point","coordinates":["45.435140","-122.761893"]},"impacting":"Y","status":"cleared","messages":{"alertCMessageCodes":[{"eventCode":"201","level":"Primary","quantifierType":"0"},{"eventCode":"520","level":"Secondary","quantifierType":"0"}],"inrixMessage":[{"inrixCode":"2","type":"Cause"},{"inrixCode":"831","type":"Effect","quantifierData":"right","quantifierType":"description"}]},"location":{"countryCode":"1","direction":"Southbound","biDirectional":"false","segments":[{"type":"XDS","offset":"432,442","code":"1236860509"}]},"schedule":{"planned":"false","advanceWarning":"false","occurrenceStartTime":"2020-12-18T02:09:46Z","occurrenceEndTime":"2020-12-18T02:50:28Z","descriptions":{"lang":"en-US","desc":"Starts at 12/17/2020 6:09 PM, ends at 12/17/2020 6:50 PM."}},"descriptions":[{"type":"short","lang":"en-US","desc":"OR-217 S/B: accident at Exit 6 OR-99W Pacific Hwy"},{"type":"long","lang":"en-US","desc":"Right lane blocked due to accident on OR-217 Southbound at Exit 6 OR-99W Pacific Hwy."},{"type":"Text-to-Speech","lang":"en-US","desc":"On OR-217 Southbound, at Exit 6 for OR-99W Pacific Highway, the right lane is blocked because of an accident."}],"parameterizedDescription":{"eventCode":"201","eventText":"Accident, (Named) Lane Blocked","roadName":"OR-217","direction":"Southbound","toLocation":"Trece","crossroad2":"OR-217  Exit 6 / OR-99W Pacific Hwy","position1":"at","position2":""},"head":{"geometry":{"type":"point","coordinates":["45.435140","-122.761893"]}},"tail":[{"geometry":{"type":"point","coordinates":["45.437844","-122.765865"]}}],"lastDetourPoints":[{"geometry":{"type":"point","coordinates":["45.437844","-122.765865"]}}],"dlrs":{"type":"XDSegment","segments":[{"id":"1236860509","offset":"432,442"}]},"rds":{"alertcMessage":"0080C9113C0049410000000000000000000000000000000000","direction":"0","extent":"0","duration":"0","diversion":"false","directionalityChanged":"false","eventCode":[{"code":"201","primary":"true"},{"code":"520","primary":"false"}]},"delayImpact":{"fromTypicalMinutes":"0.00","fromFreeFlowMinutes":"0.00","distance":"0.00"}}]}}
`