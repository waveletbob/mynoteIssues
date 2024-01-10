helm repo add apache-hadoop-helm https://pfisterer.github.io/apache-hadoop-helm/
helm pull apache-hadoop-helm/hadoop --version 1.2.0
tar -xf hadoop-1.2.0.tgz


FROM myharbor.com/bigdata/centos:7.9.2009

RUN rm -f /etc/localtime && ln -sv /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone

RUN export LANG=zh_CN.UTF-8

# 创建用户和用户组，跟yaml编排里的spec.template.spec.containers. securityContext.runAsUser: 9999
RUN groupadd --system --gid=9999 admin && useradd --system --home-dir /home/admin --uid=9999 --gid=admin admin

# 安装sudo
RUN yum -y install sudo ; chmod 640 /etc/sudoers

# 给admin添加sudo权限
RUN echo "admin ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

RUN yum -y install install net-tools telnet wget

RUN mkdir /opt/apache/

ADD jdk-8u212-linux-x64.tar.gz /opt/apache/

ENV JAVA_HOME=/opt/apache/jdk1.8.0_212
ENV PATH=$JAVA_HOME/bin:$PATH

ENV HADOOP_VERSION 3.3.2
ENV HADOOP_HOME=/opt/apache/hadoop

ENV HADOOP_COMMON_HOME=${HADOOP_HOME} \
    HADOOP_HDFS_HOME=${HADOOP_HOME} \
    HADOOP_MAPRED_HOME=${HADOOP_HOME} \
    HADOOP_YARN_HOME=${HADOOP_HOME} \
    HADOOP_CONF_DIR=${HADOOP_HOME}/etc/hadoop \
    PATH=${PATH}:${HADOOP_HOME}/bin

#RUN curl --silent --output /tmp/hadoop.tgz https://ftp-stud.hs-esslingen.de/pub/Mirrors/ftp.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && tar --directory /opt/apache -xzf /tmp/hadoop.tgz && rm /tmp/hadoop.tgz
ADD hadoop-${HADOOP_VERSION}.tar.gz /opt/apache
RUN ln -s /opt/apache/hadoop-${HADOOP_VERSION} ${HADOOP_HOME}

RUN chown -R admin:admin /opt/apache

WORKDIR $HADOOP_HOME

# Hdfs ports
EXPOSE 50010 50020 50070 50075 50090 8020 9000

# Mapred ports
EXPOSE 19888

#Yarn ports
EXPOSE 8030 8031 8032 8033 8040 8042 8088

#Other ports
EXPOSE 49707 2122
-----------------------------------
k8s搭建hadoop集群 k8s部署hadoop
https://blog.51cto.com/u_16099271/6961415