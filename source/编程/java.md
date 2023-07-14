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


## NIO

Netty\akka\rpc
selector

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



