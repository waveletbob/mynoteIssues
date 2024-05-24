# Spark

## 架构

## 模块

## 原理解析

### spark-sql执行流程

- Parser:sql解析阶段，将sql解析成AST（抽象语法树：目标语言的function）
sql模块->org.apache.spark.sql.catalyst.parser
通过ANTLR4解析翻译，自定义AST:ASTbuilder
- Optimizer:逻辑优化阶段，将AST优化成逻辑计划
org.apache.spark.sql.catalyst.optimizer/expressions
- Physical Planning物理计划生成
SparkPlanner-SparkStrategy-LogicalPlan-PhysicalPlan
- 物理计划选择（Physical Plan Selection）：
- 代码生成（Code Generation）：
- 执行（Execution）：
- 结果返回DataFrame/DataSet

### BatchWrite批量写

