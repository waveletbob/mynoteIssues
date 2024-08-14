# Doris

## 集群部署安装
- k8s
```bash
curl -o doris_follower.yml https://raw.githubusercontent.com/apache/doris/master/docker/runtime/k8s/doris_follower.yml
curl -o doris_be.yml https://raw.githubusercontent.com/apache/doris/master/docker/runtime/k8s/doris_be.yml
curl -o doris_cn.yml https://raw.githubusercontent.com/apache/doris/master/docker/runtime/k8s/doris_cn.yml

```
- docker
- 本机bin
- src编译

## 数据库连接

- mysql-client
- Arrow Flight

## 表设计

- 数据类型
- 数据模型
  - 明细Duplicate
  - 主键模型 Unique
  - 聚合模型Aggregate
- 分区&分桶
  - 分区：Range/List(例如dt,type)
  - Bucket/tablet:hash/random（解决数据倾斜）
```sql
-- Range Partition
CREATE TABLE IF NOT EXISTS example_range_tbl
(
    `user_id` LARGEINT NOT NULL COMMENT "用户id",
    `date` DATE NOT NULL COMMENT "数据灌入日期时间",
    `timestamp` DATETIME NOT NULL COMMENT "数据灌入的时间戳",
    `city` VARCHAR(20) COMMENT "用户所在城市",
    `age` SMALLINT COMMENT "用户年龄",
    `sex` TINYINT COMMENT "用户性别",
    `last_visit_date` DATETIME REPLACE DEFAULT "1970-01-01 00:00:00" COMMENT "用户最后一次访问时间",
    `cost` BIGINT SUM DEFAULT "0" COMMENT "用户总消费",
    `max_dwell_time` INT MAX DEFAULT "0" COMMENT "用户最大停留时间",
    `min_dwell_time` INT MIN DEFAULT "99999" COMMENT "用户最小停留时间"
)
ENGINE=OLAP
AGGREGATE KEY(`user_id`, `date`, `timestamp`, `city`, `age`, `sex`)
PARTITION BY RANGE(`date`)
(
    PARTITION `p201701` VALUES LESS THAN ("2017-02-01"),
    PARTITION `p201702` VALUES LESS THAN ("2017-03-01"),
    PARTITION `p201703` VALUES LESS THAN ("2017-04-01"),
    PARTITION `p2018` VALUES [("2018-01-01"), ("2019-01-01"))
)
DISTRIBUTED BY HASH(`user_id`) BUCKETS 16
PROPERTIES
(
    "replication_num" = "1"
);
```
## 数据操作
## 数据查询
## 湖仓一体
## doris管理
## 实践指南
## 周边生态

## 读写原理
- 存储结构
有序存储
稀疏索引
前缀缩影
位图索引
BloomFIlter
> 设计目标：批量导入，少量更新，绝大多数的读取，宽表，非事务，扩展性
- 读写流程





