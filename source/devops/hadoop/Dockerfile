# 使用官方 Java 镜像作为基础镜像
FROM openjdk:8-jdk


# 设置 Hadoop 版本和下载 URL
ENV HADOOP_VERSION 3.2.4
#ENV HADOOP_URL https://mirrors.tuna.tsinghua.edu.cn/apache/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz
ENV HADOOP_URL https://mirrors.tuna.tsinghua.edu.cn/apache/hadoop/common/hadoop-3.2.4/hadoop-3.2.4.tar.gz

# 下载并解压 Hadoop
RUN wget $HADOOP_URL \
#    && wget  $HADOOP_URL.asc \
#    && sha512sum -c hadoop-$HADOOP_VERSION.tar.gz.sha512 \
    && tar -xzf hadoop-$HADOOP_VERSION.tar.gz -C /opt/ \
    && rm hadoop-$HADOOP_VERSION.tar.gz*
# 安装 Java
RUN ls -l /usr/local/openjdk-8
ENV JAVA_HOME /usr/local/openjdk-8
ENV PATH $JAVA_HOME/bin:$PATH
## 配置Hadoop
#RUN echo "fs.defaultFS=hdfs://localhost:9000" > $HADOOP_HOME/etc/hadoop/core-site.xml
#RUN cat $HADOOP_HOME/etc/hadoop/core-site.xml
#RUN echo "hadoop.tmp.dir=/app/hadoop/tmp" >> $HADOOP_HOME/etc/hadoop/core-site.xml
#RUN cp $HADOOP_HOME/etc/hadoop/hdfs-site.xml $HADOOP_HOME/etc/hadoop/hdfs-site.xml.template
#RUN echo "dfs.replication=1" >> $HADOOP_HOME/etc/hadoop/hdfs-site.xml
#RUN cp $HADOOP_HOME/etc/hadoop/yarn-site.xml $HADOOP_HOME/etc/hadoop/yarn-site.xml.template
#RUN echo "yarn.nodemanager.aux-services=mapreduce_shuffle" >> $HADOOP_HOME/etc/hadoop/yarn-site.xml
#RUN echo "yarn.resourcemanager.address.hostname=localhost" >> $HADOOP_HOME/etc/hadoop/yarn-site.xml
# 设置环境变量
ENV HADOOP_HOME /opt/hadoop-$HADOOP_VERSION
ENV PATH $HADOOP_HOME/bin/:$HADOOP_HOME/sbin/:$PATH

# 工作目录设置为Hadoop目录
#WORKDIR $HADOOP_HOME
#RUN apt-get install ssh-client \
#    && ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa \
#    && cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys \
#   && chmod 0600 ~/.ssh/authorized_keys
# 格式化 Hadoop 分布式文件系统

RUN $HADOOP_HOME/bin/hdfs namenode -format

# 开放端口
EXPOSE 9870 9000 8020 8040 8088 10020 19888 50070 50075
ENV HDFS_NAMENODE_USER root
ENV HDFS_DATANODE_USER root
ENV HDFS_SECONDARYNAMENODE_USER root
# 启动 Hadoop 相关服务
CMD ["bash", "-c", "$HADOOP_HOME/sbin/start-dfs.sh && $HADOOP_HOME/sbin/start-yarn.sh && tail -f /dev/null"]
