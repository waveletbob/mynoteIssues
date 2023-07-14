# FlinkOnK8s

## FlnikOperation

1、安装Helm  

2、安装operator
```bash
kubectl create -f https://github.com/jetstack/cert-manager/releases/download/v1.8.2/cert-manager.yaml
kubectl create ns gdc
helm repo add flink-operator-repo https://downloads.apache.org/flink/flink-kubernetes-operator-1.2.0
helm install flink-kubernetes-operator flink-operator-repo/flink-kubernetes-operator --set image.repository=apache/flink-kubernetes-operator --namespace gdc
```
helm安装好后会生成operator的pod，以及Role,RoleBinding,ServiceAccount,ConfigMap等一系列资源

3、提交Flink 作业
```bash
kubectl create -f https://raw.githubusercontent.com/apache/flink-kubernetes-operator/release-1.5/examples/basic.yaml
kubectl logs -f deploy/basic-example
#如果需要添加8081端口查看作业
kubectl apply -f service.yaml
```

```yaml
kind: Service
apiVersion: v1
metadata:
  namespace: gdc
  name: my-flink-rest-service
spec:
  selector:
    app: application-example
    component: jobmanager
    type: flink-native-kubernetes
  ports:
    - name: rest
      protocol: TCP
      port: 8081
      targetPort: 8081
      nodePort: 30081
  type: NodePort
```





