# Flink
## k8s部署
Session模式
Application模式
K8s-deployment
```yml
apiVersion: apps/v1
kind: Deployment
metadata:
name: flink-jobmanager
spec:
replicas: 1
selector:
matchLabels:
app: flink
component: jobmanager
template:
metadata:
labels:
app: flink
component: jobmanager
spec:
containers:
- name: jobmanager
image: flink:1.13.0-scala_2.12
args:
- jobmanager
env:
- name: JOB_MANAGER_RPC_ADDRESS
valueFrom:
fieldRef:
fieldPath: status.podIP
ports:
- containerPort: 6123
- containerPort: 8081
volumeMounts:
- name: config-volume
mountPath: /opt/flink/conf/
volumes:
- name: config-volume
configMap:
name: flink-config
```
k8s-services
```yml
apiVersion: v1
kind: Service
metadata:
  name: flink-jobmanager
spec:
  selector:
    app: flink
    component: jobmanager
  ports:
  - name: rpc
    port: 6123
    targetPort: 6123
  - name: ui
    port: 8081
    targetPort: 8081
  type: NodePort
```
```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flink-jobmanager
spec:
  replicas: 1
  selector:
    matchLabels:
      app: flink
      component: jobmanager
  template:
    metadata:
      labels:
        app: flink
        component: jobmanager
    spec:
      containers:
      - name: jobmanager
        image: flink:1.13.0-scala_2.12
        args:
          - jobmanager
        env:
          - name: JOB_MANAGER_RPC_ADDRESS
            valueFrom:
              fieldRef:
                fieldPath: status.podIP
        ports:
        - containerPort: 6123
        - containerPort: 8081
        volumeMounts:
        - name: config-volume
          mountPath: /opt/flink/conf/
      volumes:
      - name: config-volume
        configMap:
          name: flink-config
---
apiVersion: v1
kind: Service
metadata:
  name: flink-jobmanager
spec:
  selector:
    app: flink
    component: jobmanager
  ports:
  - name: rpc
    port: 6123
    targetPort: 6123
  - name: ui
    port: 8081
    targetPort: 8081
  type: NodePort
```
```yml
opt/flink/conf/
      volumes:
      - name: config-volume
        configMap:
          name: flink-config
---
apiVersion: v1
kind: Service
metadata:
  name: flink-taskmanager
spec:
  selector:
    app: flink
    component: taskmanager
  ports:
  - name: data
    port: 6121
    targetPort: 6121
  clusterIP: None

```
```bash
#!/bin/bash

# 部署 Flink JobManager
kubectl create -f flink-jobmanager.yaml

# 等待 JobManager 启动完成
kubectl wait --for=condition=available deployment/flink-jobmanager --timeout=300s

# 部署 Flink TaskManager
kubectl create -f flink-taskmanager.yaml

# 等待 TaskManager 启动完成
kubectl wait --for=condition=ready pod -l app=flink-taskmanager --timeout=300s

# 创建 Service，将 Flink JobManager 暴露给外部
kubectl create -f flink-service.yaml

# 获取 Service 的地址和端口号
FLINK_SERVICE_HOST=$(kubectl get svc flink-service -o jsonpath="{.spec.clusterIP}")
FLINK_SERVICE_PORT=$(kubectl get svc flink-service -o jsonpath="{.spec.ports[0].port}")

# 设置 Flink 客户端的环境变量
export FLINK_JOB_MANAGER_RPC_ADDRESS=$FLINK_SERVICE_HOST
export FLINK_JOB_MANAGER_RPC_PORT=$FLINK_SERVICE_PORT

# 提交 Flink 作业
flink run myjob.jar

# 访问 Flink Web UI
echo "Flink Web UI: http://$FLINK_SERVICE_HOST:$FLINK_SERVICE_PORT"
```
## Flink client
flink run客户端

## Flink runtime

server端服务定义
## flink-streaming-java


## flink-java

## flink core


## flink connectors

外部数据存储连接
cdc: Debezium、canal、flink cdc

## flink fs

文件系统接口
## flink yarn

提交模式：
local
stantalone
yarn:session、job


## flink rpc

远程提交接口
## Flink table

启动入口：
sql-client.sh->sqlClient->start->启动终端
LocalContextUtils->LocalExecutor->start->openSession->closesession->建立连接openCli->CliClient->executeInInteractiveMode/executeInNonInteractiveMode
executeStatement->callOperation->callSelect->LocalExecutor.executeQuery->executeOperation->tEnv.executeInternal->TableEnviromentImpl->executeQueryOperation

sqlClient初始化localexecutor环境以及cliclient（call operation->Localexecutor->tableenv）

## 重点难点

- Time/Window/State/Checkpoint
- Source/Sink(RichFunction、Source、)
- Processfunction

## 调优
checkpoint:checkpoint cooridnator发送barrier到各个task，各个task根据各个算子链路依次记录下state完成1次snapshot

背压（生产和消费速率不一致导致数据消费堵塞、ck barrier对齐很慢超时失败）：动态、静态
ratio <0.1 ok;0.1~0.5 LOW;>0.5 HIGH
问题追踪：一压二查三指标，延迟吞吐是核心。时刻关注资源量 ,  排查首先看 GC

常见问题：

## rpc原理（基于akka）

rpcgateway-rpcendpoint-rpcservice-rpcserver-akkarpcservice-actorsystem
