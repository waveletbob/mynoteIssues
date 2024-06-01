FROM alpine:3.17.0 AS builder

# Download required jars
WORKDIR /tmp/download/my-jars
RUN wget https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-flink-runtime-1.16/1.4.0/iceberg-flink-runtime-1.16-1.4.0.jar
RUN wget https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.17.263/bundle-2.17.263.jar
RUN wget https://repo1.maven.org/maven2/software/amazon/awssdk/url-connection-client/2.17.263/url-connection-client-2.17.263.jar

FROM apache/flink:1.16.2-scala_2.12-java8 AS runtime

# Install Python 3.8 & git & PyFlink
RUN apt-get update && apt-get install -y software-properties-common &&  \
    add-apt-repository -y ppa:deadsnakes/ppa &&  \
    apt-get remove -y software-properties-common && apt-get autoremove -y && apt-get clean
RUN apt-get update && apt-get install -y python3.8 python3-pip python3.8-distutils git && apt-get clean
RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install apache-flink==1.16.2 --no-cache-dir

#Install Hadoop & export Hadoop classpath
WORKDIR /tmp/download/my-hadoop
RUN wget https://mirrors.tuna.tsinghua.edu.cn/apache/hadoop/common/hadoop-3.3.5/hadoop-3.3.5.tar.gz &&  \
    tar xzf hadoop-3.3.5.tar.gz &&  \
    mv hadoop-3.3.5 /opt/hadoop-3.3.5 &&  \
    rm hadoop-3.3.5.tar.gz
ENV HADOOP_HOME=/opt/hadoop-3.3.5
ENV HADOOP_CLASSPATH=/opt/hadoop-3.3.5/etc/hadoop:/opt/hadoop-3.3.5/share/hadoop/common/lib/*:/opt/hadoop-3.3.5/share/hadoop/common/*:/opt/hadoop-3.3.5/share/hadoop/hdfs:/opt/hadoop-3.3.5/share/hadoop/hdfs/lib/*:/opt/hadoop-3.3.5/share/hadoop/hdfs/*:/opt/hadoop-3.3.5/share/hadoop/mapreduce/*:/opt/hadoop-3.3.5/share/hadoop/yarn:/opt/hadoop-3.3.5/share/hadoop/yarn/lib/*:/opt/hadoop-3.3.5/share/hadoop/yarn/*

#Copy jars from builder stage
COPY --from=builder /tmp/download/my-jars/. /opt/flink/lib/.