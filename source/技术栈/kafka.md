# Kafka

## 安装

```bash
$ mkdir -p /opt/bigdata/kafka
$ cd /opt/bigdata/kafka
$ kubectl create namespace bigdata

```
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: nfs-client-provisioner
  # replace with namespace where provisioner is deployed
  namespace: bigdata        #根据实际环境设定namespace,下面类同
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: nfs-client-provisioner-runner
  namespace: bigdata
rules:
  - apiGroups: [""]
    resources: ["persistentvolumes"]
    verbs: ["get", "list", "watch", "create", "delete"]
  - apiGroups: [""]
    resources: ["persistentvolumeclaims"]
    verbs: ["get", "list", "watch", "update"]
  - apiGroups: ["storage.k8s.io"]
    resources: ["storageclasses"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["create", "update", "patch"]
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: run-nfs-client-provisioner
subjects:
  - kind: ServiceAccount
    name: nfs-client-provisioner
    namespace: bigdata
    # replace with namespace where provisioner is deployed
roleRef:
  kind: ClusterRole
  name: nfs-client-provisioner-runner
  apiGroup: rbac.authorization.k8s.io
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: leader-locking-nfs-client-provisioner
  namespace: bigdata
    # replace with namespace where provisioner is deployed
rules:
  - apiGroups: [""]
    resources: ["endpoints"]
    verbs: ["get", "list", "watch", "create", "update", "patch"]
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: leader-locking-nfs-client-provisioner
  namespace: bigdata
subjects:
  - kind: ServiceAccount
    name: nfs-client-provisioner
    # replace with namespace where provisioner is deployed
    namespace: bigdata
roleRef:
  kind: Role
  name: leader-locking-nfs-client-provisioner
  apiGroup: rbac.authorization.k8s.io
---
kind: Deployment
apiVersion: apps/v1
metadata:
  name: nfs-client-provisioner
  namespace: bigdata
spec:
  replicas: 1
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: nfs-client-provisioner
  template:
    metadata:
      labels:
        app: nfs-client-provisioner
    spec:
      serviceAccountName: nfs-client-provisioner
      containers:
        - name: nfs-client-provisioner
          image: quay.io/external_storage/nfs-client-provisioner:latest
          volumeMounts:
            - name: nfs-client-root
              mountPath: /persistentvolumes #容器内挂载点
          env:
            - name: PROVISIONER_NAME
              value: fuseim.pri/ifs
            - name: NFS_SERVER
              value: 192.168.0.113
            - name: NFS_PATH
              value: /opt/nfsdata
      volumes:
        - name: nfs-client-root #宿主机挂载点
          nfs:
            server: 192.168.0.113
            path: /opt/nfsdata
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: bigdata-nfs-storage
  namespace: bigdata
provisioner: fuseim.pri/ifs  # or choose another name, must match deployment's env PROVISIONER_NAME'
reclaimPolicy: Retain        #回收策略：Retain（保留）、 Recycle（回收）或者Delete（删除）
volumeBindingMode: Immediate    #volumeBindingMode存储卷绑定策略
allowVolumeExpansion: true    #pvc是否允许扩容
```
```shell
$ helm repo add bitnami https://charts.bitnami.com/bitnami
$ helm install zookeeper bitnami/zookeeper \
--namespace bigdata \
--set replicaCount=3 --set auth.enabled=false \
--set allowAnonymousLogin=true \
--set persistence.storageClass=bigdata-nfs-storage \
--set persistence.size=1Gi
$ kubectl get pod,pv,svc -n bigdata -o wide
$ export POD_NAME=$(kubectl get pods --namespace bigdata -l "app.kubernetes.io/name=zookeeper,app.kubernetes.io/instance=zookeeper,app.kubernetes.io/component=zookeeper" -o jsonpath="{.items[0].metadata.name}")
$ kubectl exec -it $POD_NAME -n bigdata -- zkCli.sh
# 先删掉本地端口对应的进程，要不然就得换连接端口了
$ netstat -tnlp|grep 127.0.0.1:2181|awk '{print int($NF)}'|xargs kill -9
# 外部连接测试
$ kubectl port-forward --namespace bigdata svc/zookeeper 2181:2181 &
# 需要本机安装zk客户端
$ zkCli.sh 127.0.0.1:21
$ helm status zookeeper -n bigdata
zookeeper.bigdata.svc.cluster.local
$ helm install kafka bitnami/kafka \
--namespace bigdata \
--set zookeeper.enabled=false \
--set replicaCount=3 \
--set externalZookeeper.servers=zookeeper.bigdata.svc.cluster.local \
--set persistence.storageClass=bigdata-nfs-storage
$ kubectl get pod,svc -n bigdata

```
```yaml
NAME: zookeeper
LAST DEPLOYED: Sat Dec  4 13:38:16 2021
NAMESPACE: bigdata
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: zookeeper
CHART VERSION: 7.4.13
APP VERSION: 3.7.0

** Please be patient while the chart is being deployed **

ZooKeeper can be accessed via port 2181 on the following DNS name from within your cluster:

    zookeeper.bigdata.svc.cluster.local

To connect to your ZooKeeper server run the following commands:

    export POD_NAME=$(kubectl get pods --namespace bigdata -l "app.kubernetes.io/name=zookeeper,app.kubernetes.io/instance=zookeeper,app.kubernetes.io/                           component=zookeeper" -o jsonpath="{.items[0].metadata.name}")
    kubectl exec -it $POD_NAME -- zkCli.sh

To connect to your ZooKeeper server from outside the cluster execute the following commands:

    kubectl port-forward --namespace bigdata svc/zookeeper 2181:2181 &
    zkCli.sh 127.0.0.1:2181

```
## 概念特性

## 读写优化

mmap内存地址映射
pagecache

## 副本同步机制
 水位线-leader 选举机制

## 常见问题处理

脑裂：controller出现异常选举新的导致出现两个，这是zookeeper维护了1个叫epoch-num单调递增的controller编号，旧的会被忽略

controller卡死如何处理：
这时的处理方式就是通过zookeeper的/controller节点删掉直接将controller下线，重新选举出新的controller

## 数据发送过程

send-拦截器-序列化器-分区器---缓存队列---发送线程-Sender-request-networkclient-selector


