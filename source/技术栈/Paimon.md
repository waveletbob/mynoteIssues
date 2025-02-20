# 基本概念
primary key: 主键
- 主键表。带更新
- 日志表，无主键，批处理
- 湖管控，湖仓一体
bucket 划分，类似tablelet的存储最小划分单元，一个表能用多少并发进行读写取决于其bucket数量有多少，因此在设计表模型时，除了基本的primary key,partition
等外,还需要重点考虑bucket的数量。一般情况下，是根据 'bucket'='xx'进行设置，如果没有指定，默认按照primary key或整行数据（非主键表）,bucket数量可以设置在分区上
- 写入


# 入湖

- 全自动：CDC
- 半自动：Flink、Spark

## 主键表，更新

![img_1.png](img_1.png)

## 日志表

![img_2.png](img_2.png)
![img_4.png](img_4.png)

![img_5.png](img_5.png)


## 管控
![img_3.png](img_3.png)

![img_6.png](img_6.png)







