# Springboot
- 优点：轻量。自动配置管理、web集成、jar包、本地程序启动，简化开发
- 缺点： 很多服务无法使用，如：服务发现、监控、安全管理，需要配合springcloud组件进行使用，依赖多，一个最简单的应用都有几十M，不适合小应用

- 常用注解：
  @EnableTransactionManagement
  @SpringBootApplication
  @MapperScan

## 常用包管理

- 安全：Springboot security->Shiro
- spring-boot-starter-parent 依赖父包
- spring-boot-starter-web
- spring-boot-starter
- spring-boot-starter-aop
- spring-boot-devtools
- spring-boot-starter-data-jpa
- swagger-spring-boot-starter

## RESTFul接口
- Swagger
- RestfulController

## 项目规范
1、封装业务逻辑
2、对象存储多参数
3、模块-包分类（controller、service/impl、model-dao-repositpories-entity、common、config、constant、toolkit、）
4、封装方法
5、使用常用注解：lomback、@Data..

maven多模块构建：（用户权限登陆auth、common、config、tools、功能及impl、server、client,core、etc...）
git仓库管理
src/main/java分层（utils、constant、config、entity、dao/repository/mapper/service、domain、controller-service-model（server模块）、toolkit、security）


