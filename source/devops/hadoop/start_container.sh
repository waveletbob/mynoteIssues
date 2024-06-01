#!/bin/bash

# the default node number is 3
N=${3:-1}


# start hadoop master container
#script_dir=$(dirname "$0")
#sudo podman rm -f hadoop-master &> /dev/null
#podman rmi -f hadoop-standalone
#podman build -t hadoop-standalone .
podman rm -f $(podman ps -a -q -f "name=bigdata")
echo "start hadoop-master container..."
sudo podman run -itd \
                --net=hadoop \
                -p 50070:50070 \
                -p 8088:8088 \
                -p 9000:9000 \
                --name bigdata \
                --hostname bigdata \
                --privileged \
                localhost/hadoop-standalone:latest &> /dev/null


#start hadoop slave container
i=1
while [ $i -lt 1 ]
do
	#sudo docker rm -f hadoop-slave$i &> /dev/null
	podman rm -f $(podman ps -a -q -f "name=slave$i")
	echo "start hadoop-slave$i container..."
	sudo podman run -itd \
	                --net=hadoop \
	                --name slave$i \
	                --hostname slave$i \
	                localhost/hadoop-standalone:latest &> /dev/null
	i=$(( $i + 1 ))
done

# get into hadoop master container
sudo podman exec -it bigdata bash