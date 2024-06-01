# Java

## JVM

- 内存模型（hotspot）
    - 堆
    - 栈
    - 本地内存-元空间
- 垃圾回收
    - 垃圾回收器
    - 内存分配策略
- 类加载
- class文件结构
- JVM性能参数调优
- 问题诊断工具
    - jstack
    - jmap
    - jhat
    - jstat

## 多进程高并发编程
- 并发理论
cpu-缓存-内存-IO
 原子性（多线程分时复用）、一致性（指令编排）、可见性（缓存）
 解决方案：synchronized/Lock、volatile保证有序性、Happens-Before 规则
- 线程启动方式
    - Thread
    - Runnable
    - Executors.newCachedThread
- 同步实现：
重量级synchronized、ReetrantLock、Lock（AQS）
轻量级cas-aotmic、
无同步方案: 栈封闭，Thread Local，可重入代码
- Synchronized
- volatile
- final
- ThreadLocal
- JUC
    - Aotmic
    - locks-tools
    - collections
        - ConcurrentHashMap
        - CopyOnWriteArrayList
    - exector


## 网络编程
* BIO/NIO/AIO
* Netty
  * Channel
  ![img.png](img.png)
  * ByteBuf
  ![img_1.png](img_1.png)
  * Codec
* akka
* rpc


## 基础框架

- Collections
    - List
        - Vector-Stack
        - ArrayList
        - LinkedList
    - Set
        - HashSet-LinkedHashSet
        - TreeSet
    - Queue
    - Map
        - HashMap-LinkedHashMap
        - TreeMap

- 关键字
    - static
    - abstract
    - interface
    - public/private/protected
    - Optional
    - transient

- 注解

- 反射

- 范型
    - ？ && T

## Java8
- Lambda表达式
- 引用
- 接口默认方法
- Stream
- Optional
- 函数式接口
- Nashorn, JavaScript 引擎
- 新的日期时间 API
- Base64
## SPI：java.util.ServiceLoader类服务加载
1.创建接口文件
2.resources文件夹下创建META-INF/services文件夹
3.在services文件夹中创建文件，用接口命名
4.创建接口实现类





