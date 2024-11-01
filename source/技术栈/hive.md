# MR优化参数
1、mapper time
原因：mapper数量过多，处理小文件过多，数据文件大小差异导致数据倾斜、

2

```sql
SET mapreduce.map.memory.mb=4096;
SET mapreduce.map.java.opts=-Xmx3072m;
SET dfs.blocksize=268435456;

SET hive.hadoop.supports.splittable.combineinputformat=true;
SET mapreduce.input.fileinputformat.split.maxsize=256000000;
SET mapreduce.input.fileinputformat.split.minsize.per.node=256000000;
SET mapreduce.input.fileinputformat.split.minsize.per.rack=256000000;
SET hive.input.format=org.apache.hadoop.hive.ql.io.CombineHiveInputFormat;
SET hive.merge.mapfiles=true;
SET hive.merge.mapredfiles=true;
SET hive.merge.size.per.task=256000000;
SET hive.merge.smallfiles.avgsize=256000000;

SET hive.exec.compress.intermediate=true;
SET hive.intermediate.compression.codec=org.apache.hadoop.io.compress.SnappyCodec;
SET hive.exec.compress.output=true;
SET mapred.output.compression.codec=org.apache.hadoop.io.compress.SnappyCodec;

set hive.exec.dynamic.partition.mode=nonstrict;
set hive.exec.max.dynamic.partitions=15000;
set hive.exec.max.dynamic.partitions.pernode=15000;
set hive.exec.max.created.files=250000;
```