# Docker
通用容器，云服务基本组件
多容器采用k8s编排管理
## 指令
- FROM
- WORKDIR
- ENV
- COPY
- ADD
- CMD

## dockerfile服务镜像打包

dockefile
maven插件


## docker-compose服务部署
```yml
version: '3.5'

services:
  freegpt-webui:
    image: freegpt-webui
    container_name: freegpt-webui
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "1338:1338"

```


