## 组件
* kube-apiserver：Kubernetes API 服务器，提供 Kubernetes API 的访问和管理。

* kube-controller-manager：控制器管理器，负责管理 Kubernetes 中的控制器，例如 ReplicaSet、Deployment 等。

* kube-scheduler：调度器，负责将 Pod 调度到可用的节点上运行。

* kubelet：运行在每个节点上的代理，负责管理节点上的容器和 Pod。

* kube-proxy：负责实现 Kubernetes Service 的网络代理和负载均衡。

* etcd：分布式键值存储系统，用于存储 Kubernetes 的配置和状态信息。

* kube-dns：Kubernetes 集群的 DNS 服务，提供服务发现和域名解析功能。

* CoreDNS：替代 kube-dns 的 Kubernetes 集群 DNS 服务。

* Dashboard：Kubernetes 的 Web UI，用于管理和监控 Kubernetes 集群。

* Ingress Controller：负责管理和配置 Kubernetes 集群中的 Ingress 资源，实现 HTTP/HTTPS 流量的路由和负载均衡。

* Storage Class：Kubernetes 的存储类，用于定义不同存储介质的属性和配置，例如 NFS、AWS EBS 等。

* Volume Controller：负责管理 Kubernetes 集群中的 Volume 资源，例如 Persistent Volume 和 Persistent Volume Claim。

* Helm：Kubernetes 的包管理器，用于管理和部署 Kubernetes 应用程序。

* Istio：开源的服务网格框架，用于管理和监控微服务应用程序。

## 周边组件

* Docker：开源的容器化平台，用于创建、打包和运行应用程序的容器。

* Helm Charts：Helm 的包管理文件，用于定义 Kubernetes 应用程序的部署和配置。

* Prometheus：开源的监控系统，用于收集、存储和查询应用程序的度量指标。

* Grafana：开源的数据可视化工具，用于展示应用程序的度量指标和日志数据。

* Fluentd：开源的日志收集工具，用于收集、转换和存储应用程序的日志数据。

* Elasticsearch：开源的搜索引擎和分布式数据库，用于存储和查询应用程序的日志和度量指标数据。

* Kibana：开源的数据可视化工具，用于展示 Elasticsearch 中的日志和度量指标数据。

* Jaeger：开源的分布式追踪系统，用于跟踪和分析应用程序的请求流程和性能指标。

## 名词解释

* namespace
* pod
* service
* deployment
* Persistent Volumes
* Node
* ConfiMap
