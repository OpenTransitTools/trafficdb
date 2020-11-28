PORT=8070

DIR=`dirname $0`
cd $DIR/../web/

echo http://localhost:$PORT
try:
  python -m SimpleHTTPServer $PORT
except:
  python -m http.server $PORT
