home=${HOME:-$PWD}
cmd="docker run --rm -v ${home}:${home} --net=host osgeo/gdal:ubuntu-small-latest ogr2ogr $*"
echo $cmd
eval $cmd
