export DOCKER_HOST=unix:///Users/$(whoami)/Library/Containers/com.docker.docker/Data/docker.raw.sock
docker build ./ -t flink:1.14.6
kubectl delete ns flink-standalone-session
#kubectl create ns flink-standalone-session
#kubectl apply -f ./flink-conf.yaml
#kubectl apply -f ./flink-jobmanager-service.yaml
#kubectl apply -f ./flink-jobmanager.yaml
#kubectl apply -f ./flink-taskmanager.yaml
#docker push flink:1.14.6
#kubectl run -it --rm=true --image=<your-registry>/flink:1.13.2 flink-client -- /opt/flink/bin/flink run -c <your-main-class> <your-jar-file>
