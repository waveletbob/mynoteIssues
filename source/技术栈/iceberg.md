# Iceberg

## 模块
- Nessie-类git版本管理
- Spark
- snowflake
- orc
- parquet
- pig
- open-api
- mr
- kafka-connect
- hive-runtime
- hive-metastore
- gcp/gcp-bundle
- flink
- delta-lake
- dell
- data
- core(提供基本的表操作类-方法-接口)
  - Table
    - AllDataFilesTable.java
    - AllDeleteFilesTable.java
    - AllEntriesTable.java
    - AllFilesTable
    - AllManifestsTable
  - Task
  - Schema
  - DataFile
  - ManifestFile
  - Snapshot
  - AppendFiles
  - OverwriteFiles
  - DeleteFiles
  - MERGE
  - TableOperations
  - FileIO
  - PartitionSpec
  - Transform
  - MetricsConfig
  - TableScan
  - AssignTask
  - PendingUpdate
  - WriterCommitMessage
- api
- common
- aliyun
- aws
- azure
- arrow
- guava

## metadata

- metadata.json：记录所有snap-metadata.json
- snap.avro：记录每个副本的manifest-list
- avro-manifest:每个副本每个表关联的文件以及文件的元数据



