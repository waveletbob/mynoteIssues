# 概念特性

# 读写优化

mmap内存地址映射
pagecache

# 副本同步机制
 水位线-leader 选举机制

# 常见问题处理

脑裂：controller出现异常选举新的导致出现两个，这是zookeeper维护了1个叫epoch-num单调递增的controller编号，旧的会被忽略

controller卡死如何处理：
这时的处理方式就是通过zookeeper的/controller节点删掉直接将controller下线，重新选举出新的controller

# 数据发送过程

send-拦截器-序列化器-分区器---缓存队列---发送线程-Sender-request-networkclient-selector


