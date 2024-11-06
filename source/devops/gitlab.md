# gitlab

## gitlab简介

gitlabCI提供以下功能：

- GitLab Server 后端，提供仓库管理，CI/CD
- GitLab Runner 执行器
- GitLab Executor 执行节点

## gitlab-CI/CD

.gitlab-ci.yml文件编写（模版： https://gitlab.com/gitlab-org/gitlab-foss/-/tree/master/lib/gitlab/ci/templates-foss/-/tree/master/lib/gitlab/ci/templates）

## jar自动打包CI流程

*   编写.gitlab-ci.yml,配置镜像环境，编译打包测试上传启动等stage-job
  ```yml
  stages:
  - build_base_image
  - check
  - unit_test
  - build
  - deploy
  - dev_auto_test
  - pro_auto_test
  - sync_db
  - report

variables:
  DOCKER_REGISTRY: dockerhub.com
  NCR_REGISTRY: ncr.com
  NCR_REGISTRY_DEV: ncr-dev.com
  NCR_GROUP: apimgr
  ORGANISATION: dap
  AUTH_GROUP: phoenix
  PROJECT: dep35
  AUTH_USER: _dep35
  POPO_GROUP: 2466901

# 构建基础镜像
build_base_image:
  stage: build_base_image
  tags:
    - gpxrunner
  when: manual
  only:
    refs:
      - branches
    changes:
      - misc/requirements.txt
  except:
    - tags
  script:
    - build_base_image

# 静态代码检查
sonarqube-check:
  stage: check
  image:
    name: dockerhub.com/devteam/sonar-scanner-cli:latest
    entrypoint: [ "" ]
  tags:
    - gpxrunner
  variables:
    SONAR_USER_HOME: "${CI_PROJECT_DIR}/.sonar"  # Defines the location of the analysis task cache
    GIT_DEPTH: "0"  # Tells git to fetch all the branches of the project, required by the analysis task
  cache:
    key: "${CI_JOB_NAME}"
    paths:
      - .sonar/cache
  script:
    - sonar-scanner -X -Dsonar.projectKey=${CI_PROJECT_NAMESPACE/\//.}:${CI_PROJECT_NAME}:::${CI_COMMIT_REF_NAME//\//_} -Dsonar.analysis.user=${GITLAB_USER_EMAIL} -Dsonar.exclusions=tests/**  # 如需通知到开发群，可添加参数-Dsonar.analysis.popo=1xxxxx6
  allow_failure: true

# 单元测试
unit_test:
  image: ncr.com/apimgr/dev-cloud-server:base-20240524
  stage: unit_test
  only:
    - /^feature.*/
    - /^bugfix.*/
    - /^test.*/
    - develop
  tags:
    - gpxrunner
  script:
    - export PYTHONPATH=$PYTHONPATH:./
    - export ACM_WATCH_ENDPOINT=
    - pytest --cov-report term-missing --cov=devcloud --cov-report=html:./htmlcov --html=./htmlcov/report.html --cov-report xml:coverage.xml tests/unit_test/
    - python docker/scripts/push_test_coverage_report_to_oas.py unit::${CI_COMMIT_REF_NAME/\//_}
  coverage: /^TOTAL.+?(\d+\%)$/
  artifacts:
    reports:
      cobertura: coverage.xml

# 自动化测试
dev_auto_test:
  image: ncr.com/apimgr/dev-cloud-server:base
  stage: dev_auto_test
  only:
    - develop
  tags:
    - gpxrunner
  script:
    - export PYTHONPATH=$PYTHONPATH:./
    - export TEST_AUTH_USER=${QA_AUTH_USER}
    - export TEST_AUTH_KEY=${QA_AUTH_KEY_TEST}
    - export TEST_AUTH_URL=${AUTH_URL_TEST}
    - export TEST_DEVCLOUD_URL=${TEST_DEVCLOUD_URL}
    - export SVN_USER_AUTH_USER=${SVN_USER_AUTH_USER}
    - export SVN_USER_AUTH_KEY=${SVN_USER_AUTH_KEY_TEST}
    - pytest tests/test_devcloud
  allow_failure: true


# 自动化测试
pro_auto_test:
  image: ncr.com/apimgr/dev-cloud-server:base
  stage: pro_auto_test
  only:
    - tags
  tags:
    - gpxrunner
  script:
    - export PYTHONPATH=$PYTHONPATH:./
    - export TEST_AUTH_USER=${QA_AUTH_USER}
    - export TEST_AUTH_KEY=${QA_AUTH_KEY}
    - export TEST_AUTH_URL=${AUTH_URL}
    - export TEST_DEVCLOUD_URL=${DEVCLOUD_URL}
    - export SVN_USER_AUTH_USER=${SVN_USER_AUTH_USER}
    - export SVN_USER_AUTH_KEY=${SVN_USER_AUTH_KEY}
    - pytest tests/test_devcloud
  allow_failure: true

# 构建testing镜像
build_image:
  image: dockerhub.com/webase/gpxci:latest
  stage: build
  only:
    - /^feature.*/
    - develop
    - tags
  tags:
    - gpxrunner
  allow_failure: false
  script:
    - build_image

# 构建office testing镜像
build_office_image:
  image: dockerhub.com/webase/gpxci:latest
  stage: build
  tags:
    - gpxrunner_gt
  allow_failure: false
  only:
    - develop
  script:
    - build_image

oas_document_generate:
  image: ncr.com/apimgr/dev-cloud-server:base-20240524
  stage: build
  tags:
    - gpxrunner
  script:
    - export PYTHONPATH=`pwd`
    - export ACM_WATCH_ENDPOINT=
    - python devcloud/__main__.py oas upload ${CI_COMMIT_REF_NAME//\//_}
    - echo "Document url https://apidoc.com/FlowX/${CI_COMMIT_REF_NAME//\//_}"

# Prod / Testing 环境部署
deploy:
  image: dockerhub.com/devteam/atlasx-cli:0.4.5
  stage: deploy
  only:
    refs:
      - develop
      - master
      - tags
    variables:
      - $CI_COMMIT_REF_NAME =~ /^develop$/ || $CI_COMMIT_REF_NAME =~ /^master$/ || $CI_COMMIT_REF_NAME == $CI_COMMIT_TAG
  tags:
    - gpxrunner
  script: |
    BRANCH=${CI_COMMIT_REF_NAME//\//_}
    if [ -n "$CI_COMMIT_TAG" ];then ATLASX_CODE="prod" ; elif [ "${BRANCH}" == "master" ];then ATLASX_CODE="staging" ;else ATLASX_CODE=${BRANCH//-/_} ; fi
    NOW=`date '+%s'`
    echo "CI_COMMIT_TAG: ${CI_COMMIT_TAG}"
    echo "BRANCH: ${BRANCH}"
    if [ -n "$CI_COMMIT_TAG" ];then SUPPORT_PROFILES=idc ;else SUPPORT_PROFILES=test ; fi
    if [ -n "$CI_COMMIT_TAG" ];then SUPPORT_ACM_DATA_ID="devcloud.config.support.new" ;else SUPPORT_ACM_DATA_ID="devcloud.config.support" ; fi
    if [ -n "$CI_COMMIT_TAG" ];then ENVIRONMENT=prod ;else ENVIRONMENT=develop ;fi
    if [ -n "$CI_COMMIT_TAG" ];then ACM_NAMESPACE=prod ;elif [ "${BRANCH}" == "master" ];then ACM_NAMESPACE=staging ;else ACM_NAMESPACE=test ;fi
    if [ -n "$CI_COMMIT_TAG" ];then DOMAIN='int-api-flowx.com' ;elif [ "${BRANCH}" == "master" ];then DOMAIN='int-api-flowx-staging.com' ;else DOMAIN='int-api-flowx-testing.com' ;fi
    if [ -n "$CI_COMMIT_TAG" ];then DOMAIN_IDC='api-flowx.com' ;elif [ "${BRANCH}" == "master" ];then DOMAIN_IDC='api-flowx-staging.com' ;else DOMAIN_IDC='api-flowx-testing.com' ;fi
    SERVICE_AUTH_URL=${AUTH_URL}
    if [ -n "$CI_COMMIT_TAG" ];then AUTH_URL=${AUTH_URL} ;elif [ "${BRANCH}" == "master" ];then AUTH_URL=${AUTH_URL} ;else AUTH_URL=${AUTH_URL_TEST} ;fi
    if [ -n "$CI_COMMIT_TAG" ];then APP_AUTH_KEY=${AUTH_KEY} ;elif [ "${BRANCH}" == "master" ];then APP_AUTH_KEY=${AUTH_KEY} ;else APP_AUTH_KEY=${AUTH_KEY_TEST} ;fi
    if [ -n "$CI_COMMIT_TAG" ];then NAMESPACE="production" ;elif [ "${BRANCH}" == "master" ];then NAMESPACE='staging' ;else NAMESPACE="develop" ;fi
    if [ -n "$CI_COMMIT_TAG" ];then VPC="production" ;elif [ "${BRANCH}" == "master" ];then VPC='staging' ;else VPC="develop" ;fi
    if [ -n "$CI_COMMIT_TAG" ];then labels_env="prod_group" ;elif [ "${BRANCH}" == "master" ];then labels_env='staging_group' ;else labels_env="dev_group" ;fi
    cat <<EOF | atlasx -f misc/atlasx.yaml --auth_key=${AUTH_KEY} tmpl app_apply -
    businessKind: appenv
    name: flowx_server_tpl
    code: flowx_server_tpl
    apiVersion: V2
    version: 5.8

    values: # values填写用户自定义选项值
      env: "${ENVIRONMENT}"
      server_env: "${ATLASX_CODE}"
      img_tag: "${BRANCH}"
      auth_user: ${AUTH_USER}
      auth_key: ${APP_AUTH_KEY}
      auth_url: ${AUTH_URL}
      service_auth_user: ${AUTH_USER}
      service_auth_key: ${AUTH_KEY}
      service_auth_url: ${SERVICE_AUTH_URL}
      namespace: ${NAMESPACE}
      server_version: "${NOW}"
      api_domain: ${DOMAIN}
      api_domain_idc: ${DOMAIN_IDC}
      idc_env: idc
      vpc: ${VPC}
      report_cov: 1
      acm_watch_endpoint: "${ACM_WATCH_ENDPOINT}"
      acm_namespace: "${ACM_NAMESPACE}"
      acm_service_identifier: dep35-${ACM_NAMESPACE}-devcloud
      acm_api_endpoint: "${ACM_API_ENDPOINT}"
      acm_group: "${ACM_GROUP}"
      acm_data_id: devcloud.config
      labels_env: ${labels_env}
      profile: ${SUPPORT_PROFILES}
      support_acm_data_id: ${SUPPORT_ACM_DATA_ID}
      support_img_tag: "20241022"
    sys:
      code: server_${ATLASX_CODE}
      name: server_${ATLASX_CODE}
      description: dev_cloud_server_${ATLASX_CODE}
      projectcode: dep35
      projectname: 研发流水线
      usercorp: _dep35
      username: _dep35
      env: idc
    EOF
    echo '... check deploy status ...'
    sh scripts/atlasx/check_atlasx_deploy_status.sh server_${ATLASX_CODE}
    echo 'atlasx deploy done'

# Prod / Testing 环境部署
deploy_celery_worker:
  image: dockerhub.com/devteam/atlasx-cli:0.4.5
  stage: deploy
  only:
    refs:
      - develop
      - tags
    variables:
      - $CI_COMMIT_REF_NAME =~ /^develop$/ || $CI_COMMIT_REF_NAME == $CI_COMMIT_TAG
  tags:
    - gpxrunner
  script: |
    BRANCH=${CI_COMMIT_REF_NAME//\//_}
    if [ -n "$CI_COMMIT_TAG" ];then ATLASX_CODE="Prod" ; else ATLASX_CODE="Testing" ; fi
    ENVIRONMENT=${BRANCH//_/-}
    NOW=`date '+%s'`
    echo "CI_COMMIT_TAG: ${CI_COMMIT_TAG}"
    if [ -n "$CI_COMMIT_TAG" ];then ACM_NAMESPACE=prod ;else ACM_NAMESPACE=test ;fi
    if [ -n "$CI_COMMIT_TAG" ];then DOMAIN='int-api-flowx.com' ;else DOMAIN='int-api-flowx-testing.com' ;fi
    if [ -n "$CI_COMMIT_TAG" ];then DOMAIN_IDC='api-flowx.com' ;else DOMAIN_IDC='api-flowx-testing.com' ;fi
    if [ -n "$CI_COMMIT_TAG" ];then NAMESPACE="production" ;else NAMESPACE="develop" ;fi
    if [ -n "$CI_COMMIT_TAG" ];then VPC="production" ;else VPC="develop" ;fi
    SERVICE_AUTH_URL=${AUTH_URL}
    if [ -n "$CI_COMMIT_TAG" ];then AUTH_URL=${AUTH_URL} ;else AUTH_URL=${AUTH_URL_TEST} ;fi
    if [ -n "$CI_COMMIT_TAG" ];then APP_AUTH_KEY=${AUTH_KEY} ;else APP_AUTH_KEY=${AUTH_KEY_TEST} ;fi
    cat <<EOF | atlasx -f misc/atlasx.yaml --auth_key=${AUTH_KEY} tmpl app_apply -
    businessKind: appenv
    name: devcloud_celery_worker
    code: devcloud_celery_worker
    OAMVersion: V2
    version: 1.4

    values: # values填写用户自定义选项值
      img_tag: "${BRANCH}"
      auth_user: ${AUTH_USER}
      auth_key: ${APP_AUTH_KEY}
      auth_url: ${AUTH_URL}
      service_auth_user: ${AUTH_USER}
      service_auth_key: ${AUTH_KEY}
      service_auth_url: ${SERVICE_AUTH_URL}
      namespace: ${NAMESPACE}
      server_version: "${NOW}"
      server_env: testing
      api_domain: ${DOMAIN}
      api_domain_idc: ${DOMAIN_IDC}
      idc_env: idc
      vpc: ${VPC}
      acm_watch_endpoint: "${ACM_WATCH_ENDPOINT}"
      acm_namespace: "${ACM_NAMESPACE}"
      acm_service_identifier: dep35-${ACM_NAMESPACE}-devcloud
      acm_api_endpoint: "${ACM_API_ENDPOINT}"
      acm_group: "${ACM_GROUP}"
      acm_data_id: devcloud.celery.config
      labels_env: ${labels_env}
    sys:
      code: DevcloudCeleryWorker${ATLASX_CODE}
      name: DevcloudCeleryWorker${ATLASX_CODE}
      description: ''
      projectcode: dep35
      usercorp: gzzhangyi2015
      username: 张怡
      env: idc
    EOF
    echo '... check deploy status ...'
    sh scripts/atlasx/check_atlasx_deploy_status.sh DevcloudCeleryWorker${ATLASX_CODE}
    echo 'atlasx deploy done'


deploy_kafka:
  image: dockerhub.com/devteam/atlasx-cli:0.4.5
  stage: deploy
  when: manual
  only:
    refs:
      - develop
      - tags
    variables:
      - $CI_COMMIT_REF_NAME =~ /^develop$/ || $CI_COMMIT_REF_NAME == $CI_COMMIT_TAG
  tags:
    - gpxrunner
  script: |
    BRANCH=${CI_COMMIT_REF_NAME//\//_}
    if [ -n "$CI_COMMIT_TAG" ];then ATLASX_CODE="prod" ; else ATLASX_CODE=${BRANCH//-/_} ; fi
    ENVIRONMENT=${BRANCH//_/-}
    NOW=`date '+%s'`
    echo "CI_COMMIT_TAG: ${CI_COMMIT_TAG}"
    if [ -n "$CI_COMMIT_TAG" ];then ACM_NAMESPACE=prod ;else ACM_NAMESPACE=test ;fi
    if [ -n "$CI_COMMIT_TAG" ];then DOMAIN='int-api-flowx.com' ;else DOMAIN='int-api-flowx-testing.com' ;fi
    if [ -n "$CI_COMMIT_TAG" ];then DOMAIN_IDC='api-flowx.com' ;else DOMAIN_IDC='api-flowx-testing.com' ;fi
    if [ -n "$CI_COMMIT_TAG" ];then NAMESPACE="production" ;else NAMESPACE="develop" ;fi
    if [ -n "$CI_COMMIT_TAG" ];then VPC="production" ;else VPC="develop" ;fi
    SERVICE_AUTH_URL=${AUTH_URL}
    if [ -n "$CI_COMMIT_TAG" ];then AUTH_URL=${AUTH_URL} ;else AUTH_URL=${AUTH_URL_TEST} ;fi
    if [ -n "$CI_COMMIT_TAG" ];then APP_AUTH_KEY=${AUTH_KEY} ;else APP_AUTH_KEY=${AUTH_KEY_TEST} ;fi
    cat <<EOF | atlasx -f misc/atlasx.yaml --auth_key=${AUTH_KEY} tmpl app_apply -
    businessKind: appenv
    name: FlowX-Kafka服务模板
    code: flowx_kafka_tpl
    apiVersion: V2
    version: 1

    values: # values填写用户自定义选项值
      env: "${ENVIRONMENT}"
      img_tag: "${BRANCH}"
      auth_user: ${AUTH_USER}
      auth_key: ${APP_AUTH_KEY}
      auth_url: ${AUTH_URL}
      service_auth_user: ${AUTH_USER}
      service_auth_key: ${AUTH_KEY}
      service_auth_url: ${SERVICE_AUTH_URL}
      namespace: ${NAMESPACE}
      server_version: "${NOW}"
      server_env: auth-kafka-consumer
      api_domain: ${DOMAIN}
      api_domain_idc: ${DOMAIN_IDC}
      idc_env: idc
      vpc: ${VPC}
      report_cov: 1
      acm_watch_endpoint: "${ACM_WATCH_ENDPOINT}"
      acm_namespace: "${ACM_NAMESPACE}"
      acm_service_identifier: dep35-${ACM_NAMESPACE}-kafka-devcloud
      acm_api_endpoint: "${ACM_API_ENDPOINT}"
      acm_group: "${ACM_GROUP}"
      acm_data_id: devcloud.kafka.config
    sys:
      code: kafkaServer${ATLASX_CODE}
      name: kafkaServer${ATLASX_CODE}
      description: dev_cloud_kafka_server_${ATLASX_CODE}
      projectcode: dep35
      projectname: 研发流水线
      usercorp: _dep35
      username: _dep35
      env: idc
    EOF
    echo '... check deploy status ...'
    sh scripts/atlasx/check_atlasx_deploy_status.sh server_${ATLASX_CODE}
    echo 'atlasx deploy done'


# 环境部署 office
deploy_office:
  image: dockerhub.com/devteam/atlasx-cli:0.4.5
  stage: deploy
  when: manual
  only:
    - develop
    - tags
  tags:
    - gpxrunner_gt
  script: |
    BRANCH=${CI_COMMIT_REF_NAME//\//_}
    ATLASX_CODE="prod"
    ENVIRONMENT="prod"
    NOW=`date '+%s'`
    echo "CI_COMMIT_TAG: ${CI_COMMIT_TAG}"
    DOMAIN='office-api-flowx.com'
    NAMESPACE="office-production"
    cat <<EOF | atlasx -f misc/atlasx_office.yaml --auth_key=${AUTH_KEY} tmpl app_apply -
    businessKind: appenv
    name: flowx_server_tpl
    code: flowx_server_tpl
    apiVersion: V2
    version: 3.4

    values: # values填写用户自定义选项值
      env: "${ENVIRONMENT}"
      server_env: "${ATLASX_CODE}"
      img_tag: "${BRANCH}"
      auth_user: ${AUTH_USER}
      auth_key: ${AUTH_KEY}
      auth_url: ${AUTH_URL}
      service_auth_user: ${AUTH_USER}
      service_auth_key: ${AUTH_KEY}
      service_auth_url: ${AUTH_URL}
      namespace: ${NAMESPACE}
      server_version: "${NOW}"
      api_domain: ${DOMAIN}
      acm_watch_endpoint: "${ACM_WATCH_ENDPOINT_OFFICE}"
      acm_namespace: dev
      acm_service_identifier: dep35-dev-devcloud
      acm_api_endpoint: "${ACM_API_ENDPOINT_OFFICE}"
      acm_group: "${ACM_GROUP}"
      acm_data_id: devcloud.config
      profile: office
      support_acm_data_id: devcloud.config.support.new
      support_img_tag: "20241022"
    sys:
      code: server_office_${ATLASX_CODE}
      name: server_office_${ATLASX_CODE}
      description: dev_cloud_server_office_${ATLASX_CODE}
      projectcode: dep35
      projectname: 研发流水线
      usercorp: _dep35
      username: _dep35
      env: office
    EOF
    echo 'atlasx office deploy done'

deploy_feature:
  image: dockerhub.com/devteam/atlasx-cli:0.4.5
  stage: deploy
  when: manual
  only:
    - /^feature.*/
  tags:
    - gpxrunner
  script: |
    BRANCH=${CI_COMMIT_REF_NAME//\//_}
    GIT_USER=`echo $GITLAB_USER_EMAIL | awk -F @ '{ print $1 }'`
    if [ -n "$CI_COMMIT_TAG" ];then ATLASX_CODE="prod" ; else ATLASX_CODE=${BRANCH//-/_} ; fi
    ENVIRONMENT=${BRANCH//_/-}
    NOW=`date '+%s'`
    echo "CI_COMMIT_TAG: ${CI_COMMIT_TAG}"
    if [ -n "$CI_COMMIT_TAG" ];then DOMAIN='int-api-flowx.com' ;else DOMAIN='int-api-flowx-testing.com' ;fi
    if [ -n "$CI_COMMIT_TAG" ];then DOMAIN_IDC='api-flowx.com' ;else DOMAIN_IDC='api-flowx-testing.com' ;fi
    if [ -n "$CI_COMMIT_TAG" ];then NAMESPACE="production" ;else NAMESPACE="develop" ;fi
    if [ -n "$CI_COMMIT_TAG" ];then VPC="production" ;else VPC="develop" ;fi
    cat <<EOF | atlasx -f misc/atlasx.yaml --auth_key=${AUTH_KEY} tmpl app_apply -
    businessKind: appenv
    name: flowx_server_tpl
    code: flowx_server_tpl
    apiVersion: V2
    version: 5.8

    values: # values填写用户自定义选项值
      env: ${GIT_USER}
      server_env: "server-${GIT_USER}"
      img_tag: "${BRANCH}"
      auth_user: ${AUTH_USER}
      auth_key: ${AUTH_KEY_TEST}
      auth_url: ${AUTH_URL_TEST}
      service_auth_user: ${AUTH_USER}
      service_auth_key: ${AUTH_KEY}
      service_auth_url: ${AUTH_URL}
      namespace: ${NAMESPACE}-${GIT_USER}
      server_version: "${NOW}"
      api_domain: ${GIT_USER}-${DOMAIN}
      api_domain_idc: ${GIT_USER}-${DOMAIN_IDC}
      idc_env: idc
      vpc: ${VPC}
      acm_watch_endpoint: "${ACM_WATCH_ENDPOINT}"
      acm_namespace: dev
      acm_service_identifier: dep35-dev-devcloud-${GIT_USER}
      acm_api_endpoint: "${ACM_API_ENDPOINT}"
      acm_group: "${ACM_GROUP}"
      acm_data_id: devcloud.config.${GIT_USER}
      labels_env: dev_group
      profile: dev
      support_acm_data_id: devcloud.config.event.${GIT_USER}
      support_img_tag: "20241022"
    sys:
      code: server_${GIT_USER}
      name: server_${GIT_USER}
      description: dev_cloud_server_${GIT_USER}
      projectcode: dep35
      projectname: 研发流水线
      usercorp: _dep35
      username: _dep35
      env: idc
    EOF
    echo '... check deploy status ...'
    ls
    sh scripts/atlasx/check_atlasx_deploy_status.sh server_${GIT_USER}
    echo 'atlasx deploy done'

deploy_kafka_feature:
  image: dockerhub.com/devteam/atlasx-cli:0.4.5
  stage: deploy
  when: manual
  only:
    - /^feature.*/
  tags:
    - gpxrunner
  script: |
    BRANCH=${CI_COMMIT_REF_NAME//\//_}
    GIT_USER=`echo $GITLAB_USER_EMAIL | awk -F @ '{ print $1 }'`
    if [ -n "$CI_COMMIT_TAG" ];then ATLASX_CODE="prod" ; else ATLASX_CODE=${BRANCH//-/_} ; fi
    ENVIRONMENT=${BRANCH//_/-}
    NOW=`date '+%s'`
    echo "CI_COMMIT_TAG: ${CI_COMMIT_TAG}"
    if [ -n "$CI_COMMIT_TAG" ];then DOMAIN='int-api-flowx.com' ;else DOMAIN='int-api-flowx-testing.com' ;fi
    if [ -n "$CI_COMMIT_TAG" ];then DOMAIN_IDC='api-flowx.com' ;else DOMAIN_IDC='api-flowx-testing.com' ;fi
    if [ -n "$CI_COMMIT_TAG" ];then NAMESPACE="production" ;else NAMESPACE="develop" ;fi
    if [ -n "$CI_COMMIT_TAG" ];then VPC="production" ;else VPC="develop" ;fi
    cat <<EOF | atlasx -f misc/atlasx.yaml --auth_key=${AUTH_KEY} tmpl app_apply -
    businessKind: appenv
    name: FlowX-Kafka服务模板
    code: flowx_kafka_tpl
    apiVersion: V2
    version: 1

    values: # values填写用户自定义选项值
      env: ${GIT_USER}
      img_tag: "${BRANCH}"
      auth_user: ${AUTH_USER}
      auth_key: ${AUTH_KEY_TEST}
      auth_url: ${AUTH_URL_TEST}
      service_auth_user: ${AUTH_USER}
      service_auth_key: ${AUTH_KEY}
      service_auth_url: ${AUTH_URL}
      namespace: ${NAMESPACE}-${GIT_USER}
      server_version: "${NOW}"
      api_domain: ${GIT_USER}-${DOMAIN}
      api_domain_idc: ${GIT_USER}-${DOMAIN_IDC}
      idc_env: idc
      vpc: ${VPC}
      acm_watch_endpoint: "${ACM_WATCH_ENDPOINT}"
      acm_namespace: dev
      acm_service_identifier: dep35-dev-devcloud-kafka-${GIT_USER}
      acm_api_endpoint: "${ACM_API_ENDPOINT}"
      acm_group: "${ACM_GROUP}"
      acm_data_id: devcloud.kafka.config.${GIT_USER}
    sys:
      code: kafkaServer${GIT_USER}
      name: kafkaServer${GIT_USER}
      description: dev_cloud_kafka_server_${GIT_USER}
      projectcode: dep35
      projectname: 研发流水线
      usercorp: _dep35
      username: _dep35
      env: idc
    EOF
    echo '... check deploy status ...'
    ls
    sh scripts/atlasx/check_atlasx_deploy_status.sh server_${GIT_USER}
    echo 'atlasx deploy done'


sync_db:
  image: ncr.com/apimgr/dev-cloud-server:base-20240524
  stage: sync_db
  when: manual
  only:
    - /^feature.*/
  tags:
    - gpxrunner
  script:
    - GIT_USER=`echo $GITLAB_USER_EMAIL | awk -F @ '{ print $1 }'`
    - python docker/scripts/sync_db.py ${GIT_USER}-int-api-flowx-testing.com

# 重启环境，触发覆盖率报告生成并提交
# 内容基本与deploy一致，只是少传一个环节变量，这样不会触发测试覆盖率报告的提交
trigger_coverage_report:
  image: dockerhub.com/devteam/atlasx-cli:0.4.5
  stage: report
  only:
    - develop
  tags:
    - gpxrunner
  script: |
    BRANCH=${CI_COMMIT_REF_NAME//\//_}
    if [ -n "$CI_COMMIT_TAG" ];then ATLASX_CODE="prod" ; else ATLASX_CODE=${BRANCH//-/_} ; fi
    ENVIRONMENT=${BRANCH//_/-}
    NOW=`date '+%s'`
    echo "CI_COMMIT_TAG: ${CI_COMMIT_TAG}"
    MONGO_DB='dev_cloud'
    if [ -n "$CI_COMMIT_TAG" ];then DOMAIN='int-api-flowx.com' ;else DOMAIN='int-api-flowx-testing.com' ;fi
    if [ -n "$CI_COMMIT_TAG" ];then DOMAIN_IDC='api-flowx.com' ;else DOMAIN_IDC='api-flowx-testing.com' ;fi
    if [ -n "$CI_COMMIT_TAG" ];then NAMESPACE="production" ;else NAMESPACE="develop" ;fi
    if [ -n "$CI_COMMIT_TAG" ];then VPC="production" ;else VPC="develop" ;fi
    if [ -n "$CI_COMMIT_TAG" ];then ACM_NAMESPACE=prod ;else ACM_NAMESPACE=test ;fi
    SERVICE_AUTH_URL=${AUTH_URL}
    if [ -n "$CI_COMMIT_TAG" ];then AUTH_URL=${AUTH_URL} ;else AUTH_URL=${AUTH_URL_TEST} ;fi
    if [ -n "$CI_COMMIT_TAG" ];then APP_AUTH_KEY=${AUTH_KEY} ;else APP_AUTH_KEY=${AUTH_KEY_TEST} ;fi
    cat <<EOF | atlasx -f misc/atlasx.yaml --auth_key=${AUTH_KEY} tmpl app_apply -
    businessKind: appenv
    name: flowx_server_tpl
    code: flowx_server_tpl
    apiVersion: V2
    version: 5.8

    values: # values填写用户自定义选项值
      env: "${ENVIRONMENT}"
      server_env: "${ATLASX_CODE}"
      img_tag: "${BRANCH}"
      auth_user: ${AUTH_USER}
      auth_key: ${APP_AUTH_KEY}
      auth_url: ${AUTH_URL}
      service_auth_user: ${AUTH_USER}
      service_auth_key: ${AUTH_KEY}
      service_auth_url: ${SERVICE_AUTH_URL}
      namespace: ${NAMESPACE}
      server_version: "${NOW}"
      api_domain: ${DOMAIN}
      api_domain_idc: ${DOMAIN_IDC}
      idc_env: idc
      vpc: ${VPC}
      acm_watch_endpoint: "${ACM_WATCH_ENDPOINT}"
      acm_namespace: "${ACM_NAMESPACE}"
      acm_service_identifier: dep35-${ACM_NAMESPACE}-devcloud
      acm_api_endpoint: "${ACM_API_ENDPOINT}"
      acm_group: "${ACM_GROUP}"
      acm_data_id: devcloud.config
      labels_env: dev_group
      profile: test
      support_acm_data_id: "devcloud.config.support"
      support_img_tag: "20241022"
    sys:
      code: server_${ATLASX_CODE}
      name: server_${ATLASX_CODE}
      description: dev_cloud_server_${ATLASX_CODE}
      projectcode: dep35
      projectname: 研发流水线
      usercorp: _dep35
      username: _dep35
      env: idc
    EOF
    echo '... check deploy status ...'
    sh scripts/atlasx/check_atlasx_deploy_status.sh server_${ATLASX_CODE}
    echo 'atlasx deploy done'



deploy_feature_front:
  image: dockerhub.com/devteam/-cli:0.4.5
  stage: deploy
  when: manual
  only:
    - /^feature.+$/
  tags:
    - gpxrunner
  script: |
    BRANCH=${CI_COMMIT_REF_NAME//\//_}
    if [ -n "$CI_COMMIT_TAG" ];then ATLASX_CODE="prod" ; else ATLASX_CODE=${BRANCH//-/_} ; fi
    GIT_USER=`echo $GITLAB_USER_EMAIL | awk -F @ '{ print $1 }'`
    ATLASX_CODE=${GIT_USER}
    NOW=`date '+%s'`
    AUTH_URL="http://int.test-auth.com"
    DOMAIN='flowx-testing.com'
    if [ -n "$CI_COMMIT_TAG" ];then AUTH_URL=${AUTH_URL} ;else AUTH_URL=${AUTH_URL_TEST} ;fi

    cat <<EOF | atlasx -f misc/atlasx.yaml --auth_key=${AUTH_KEY} tmpl app_apply -
    businessKind: appenv
    name: flowx_ui_tpl
    code: flowx_ui_tpl
    apiVersion: V2
    version: 1

    values: # values填写用户自定义选项值
      env: ${ATLASX_CODE}
      auth_url: ${AUTH_URL_TEST}
      dev_cloud_api_url: http://${GIT_USER}-int-api-${DOMAIN}
      ui_version: "${NOW}"
      lbc_domain: ${GIT_USER}-${DOMAIN}
      img_tag: "master"
    sys:
      code: ui_${ATLASX_CODE}_${GIT_USER}
      name: ui_${ATLASX_CODE}_${GIT_USER}
      description: dev_cloud_ui_${ATLASX_CODE}_${GIT_USER}
      projectcode: dep35
      projectname: 研发流水线
      usercorp: _dep35
      username: _dep35
      env: idc
    EOF
    echo 'atlasx deploy done'

.auto_devops: &auto_devops |
  REPO=`echo $CI_PROJECT_DIR | awk -F '/' '{print $NF}'`
  GROUP="$NCR_GROUP"
  DOCKER_REPO="$GROUP/$REPO"
  base_image=${NCR_REGISTRY}/$DOCKER_REPO:base
  BRANCH=${CI_COMMIT_REF_NAME//\//_}
  if [ "$CI_JOB_NAME" == "build_office_image" ];then REGISTRY=$NCR_REGISTRY_DEV ;else REGISTRY=$NCR_REGISTRY ;fi
  echo "REGISTRY: ${REGISTRY}"
  branch_image=${REGISTRY}/$DOCKER_REPO:$BRANCH

  # docker login
  function docker_login() {
    docker login -u $DOCKER_USER -p $DOCKER_PASSWORD $DOCKER_REGISTRY
    if [ "$CI_JOB_NAME" == "build_office_image" ];then
      # 高唐环境下，才能login ncr-dev
      docker login -u $NCR_USER -p $NCR_PASSWORD $NCR_REGISTRY_DEV
    fi
    docker login -u $NCR_USER -p $NCR_PASSWORD $NCR_REGISTRY
  }

  function build_base_image() {
    docker_login
    docker build --no-cache -f docker/Dockerfile_base -t $base_image .
    docker push $base_image
  }
  function build_image() {
    docker_login
    echo 'building image'
    # pull base
    docker pull $base_image

    if [ "$BRANCH" == "develop" ]
    then
      echo 'docker build --no-cache -f docker/Dockerfile_testing -t $branch_image .'
      docker build --no-cache -f docker/Dockerfile_testing -t $branch_image .
    else
      echo 'docker build -f docker/Dockerfile -t $branch_image .'
      docker build -f docker/Dockerfile -t $branch_image .
    fi
    docker push $branch_image
  }

before_script:
  - *auto_devops

  ```
- 构建docker镜像并设置maven缓存
- 提交代码并自动构建gitlab-runner

## docker自动构建镜像并推送到仓库-python

Dockerfile：
```yaml
FROM xxx

ADD ./misc/sources.list /etc/apt/sources.list
ADD ./misc/pip.conf /root/.pip/pip.conf
ADD ./misc/requirements.txt /tmp/requirements.txt

RUN pip install -U setuptools
RUN apt-get update
RUN apt-get install xx xx1-dev -y
RUN pip install -r /tmp/requirements.txt

ADD ./ /path/to/wordir
WORKDIR /path/to/wordir
EXPOSE 9098
ENV LANG C.UTF-8

```

gitlab-ci/cd.yml：
```yaml
stages:
  - build

variables:
  GIT_DOMAIN: https://gitlab.com
  DOCKER_REGISTRY: dockerhub.com

# 构建镜像
build_image:
  image: docker.com/web/python:latest
  only:
    - tags
    - develop
  stage: build
  script:
    - run_build_image

# 处理函数
.auto_devops: &auto_devops |
  function run_build_image() {
        echo building image
        docker login -u $DOCKER_USER -p $DOCKER_TOKEN $DOCKER_REGISTRY
        BRANCH=${CI_COMMIT_REF_NAME//\//-}
        REPO=$(echo $CI_PROJECT_DIR | awk -F '/' '{print $NF}')
        GROUP=$(echo $CI_PROJECT_DIR | awk -F '/' '{print $(NF-1)}')
        DOCKER_REPO="$GROUP/$REPO"
        branch_image=${DOCKER_REGISTRY}/$DOCKER_REPO:$BRANCH
        echo docker build -t $branch_image .
        docker build -t $branch_image .
        docker push $branch_image
  }

before_script:
  - *auto_devops
```