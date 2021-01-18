DIR=`dirname $0`

echo kill, rm and down containers
docker kill $(docker ps -aq)
docker container rm $(docker ps -a -q)
docker-compose down
wait;

if [[ $1 == 'ALL' ]]
then
    echo NUKE all images and containers
    echo
    docker ps --all --quiet --no-trunc --filter "status=exited" | xargs --no-run-if-empty docker rm
    docker images --quiet --filter "dangling=true" | xargs --no-run-if-empty docker rmi
    docker rmi $(docker images -q)
    docker volume ls | awk '{print $2}' | xargs docker volume rm
    echo
    echo
    docker ps
    echo
    echo
    docker images
    echo
    echo
    docker volume ls
    echo
    echo
fi
