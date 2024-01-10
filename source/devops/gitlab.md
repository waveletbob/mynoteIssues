# gitlab

## gitlab简介

gitlabCI提供以下功能：

- GitLab Server 后端，提供仓库管理，CI/CD
- GitLab Runner 执行器
- GitLab Executor 执行节点

## gitlab-CI/CD

.gitlab-ci.yml文件编写

## jar自动打包CI流程

*   编写.gitlab-ci.yml,配置镜像环境，编译打包测试上传启动等stage-job
  ```yml
  
#当前流水线所需要的镜像环境
image: xxx

#缓存，gitlab流水线会将安装的node包移除，需要设置缓存
#cache:
#  key: node_modules
#  paths:
#    - node_modules
before_script:
  - java -version
  - git version

# 任务阶段，默认的有 .pre 、 build 、 test 、deploy 、.post(执行有先后顺序)
# 也可以自定义阶段，自己定义的阶段，执行顺序是从上往下依次执行
# 例如下面的例子job_2会比jon_1先执行
stages:
  - build
# 具体的任务  
build_stage:
  tags:
    - runner-saas
  stage: build #任务阶段，可不定义，从全局的stages里面取，如果没有定义则从默认的stages里面取
  script:   #执行的脚本
#    - mvn clean package docker:build -DpushImage
    - mvn clean package
    - ls
    - git add ./target/gaia-etl-1.0-SNAPSHOT.jar
    - git add ./lib
    - git commit -m "代码自动提交"
    - git push origin master
  retry: 1  #任务失败后重试的次数
  ```
- 构建docker镜像并设置maven缓存
- 提交代码并自动构建gitlab-runner



