export DOCKER_HOST=unix:///Users/$(whoami)/Library/Containers/com.docker.docker/Data/docker.raw.sock
docker build ./ -t flink-local:1.13.2
kubectl create ns flink-local

