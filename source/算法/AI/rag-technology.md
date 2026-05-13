# 检索增强生成 (RAG) 技术

## 核心流程

```
用户查询 → Embedding → 向量检索 → Top-K 文档 → Prompt 拼装 → LLM 生成答案
```

## 文档处理

| 步骤 | 要点 | 工具 |
|------|------|------|
| **解析** | PDF/Word/Markdown/代码 | LangChain Document Loaders |
| **分块** | 大小 500-1500 tokens, overlap 10-20% | RecursiveCharacterTextSplitter |
| **Embedding** | 文本转向量 | text-embedding-3、bge-large、m3e |
| **入库** | 持久化存储 | FAISS(本地)、ChromaDB(轻量)、Milvus(生产) |

## 向量数据库选型

| 数据库 | 适用 | 特点 |
|--------|------|------|
| FAISS | 本地开发/研究 | Meta 出品，纯向量检索，需自行持久化 |
| ChromaDB | 原型/小项目 | 开箱即用，自带持久化，Python 原生 |
| Milvus | 生产环境 | 分布式，支持混合检索，K8s 部署 |
| Elasticsearch | 已有 ES 的团队 | 全文+向量混合检索 |

## 检索优化

| 技术 | 作用 | 方法 |
|------|------|------|
| **混合检索** | 关键词+语义互补 | BM25 + 向量，加权融合 |
| **重排序 (Rerank)** | 提升 Top-K 精度 | bge-reranker、Cohere Rerank |
| **查询重写** | 用户问题转检索用句 | LLM 改写 + 关键词提取 |
| **多路召回** | 不同粒度互补 | 句子级 + 段落级同时检索 |

## 代码框架

### LangChain 快速搭建

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA

vectorstore = FAISS.from_documents(docs, OpenAIEmbeddings())
qa = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())
answer = qa.run("你的问题")
```

### LlamaIndex 快速搭建

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

docs = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(docs)
answer = index.as_query_engine().query("你的问题")
```

## 实践踩坑

- **分块太小** → 丢失上下文。代码文件建议 1000+ tokens
- **分块太大** → 检索精度下降，LLM 上下文浪费
- **只用向量检索** → 精确匹配（如 ID、编号）搜不到 → 加 BM25
- **不设 top_k 上限** → 命中太多无关文档 → k=3~5 够用
- **不做评估** → 不知道改什么 → 用 RAGAS 框架评估

---

*最后更新: 2026年5月*
