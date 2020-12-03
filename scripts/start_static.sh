PORT=8000

DIR=`dirname $0`
cd $DIR/../docs/

URL=http://localhost:$PORT/map.html#10.00/45.48/-122.68/0/20
echo $URL
python -m webbrowser $URL
try:
  python -m SimpleHTTPServer $PORT
except:
  python -m http.server $PORT
