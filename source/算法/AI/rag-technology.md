# 检索增强生成 (RAG) 技术

## RAG概述

检索增强生成（Retrieval-Augmented Generation，RAG）是一种结合了检索和生成的AI技术，通过检索外部知识库来增强大语言模型的生成能力。

## 核心架构

### 基本架构

```
用户查询 → 检索器 → 相关文档 → LLM → 回答
            ↑
        向量数据库
```

### 详细流程

1. **文档索引**: 将文档分块并转换为向量
2. **向量检索**: 根据查询检索相关文档
3. **上下文构建**: 将检索结果与查询组合
4. **答案生成**: LLM基于上下文生成答案

## 文档处理

### 文档分块

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 创建分块器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # 每块大小
    chunk_overlap=200,  # 重叠大小
    length_function=len,
    separators=["\n\n", "\n", "。", "！", "？", " ", ""]
)

# 分块文档
documents = text_splitter.split_documents(raw_documents)
print(f"分块数量: {len(documents)}")
```

### 文档嵌入

```python
from sentence_transformers import SentenceTransformer

# 加载嵌入模型
embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 生成嵌入
embeddings = embedder.encode(documents, show_progress_bar=True)

print(f"嵌入维度: {embeddings.shape[1]}")
print(f"文档数量: {embeddings.shape[0]}")
```

## 向量数据库

### FAISS

```python
import faiss
import numpy as np

# 创建索引
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)

# 添加向量
index.add(embeddings.astype('float32'))

# 搜索
query_embedding = embedder.encode(["用户查询"])
k = 5  # 返回前5个结果
distances, indices = index.search(query_embedding.astype('float32'), k)

# 获取相关文档
retrieved_docs = [documents[i] for i in indices[0]]
```

### ChromaDB

```python
import chromadb
from chromadb.config import Settings

# 创建客户端
client = chromadb.Client(Settings())

# 创建集合
collection = client.create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}
)

# 添加文档
collection.add(
    documents=[doc.page_content for doc in documents],
    metadatas=[doc.metadata for doc in documents],
    ids=[str(i) for i in range(len(documents))]
)

# 查询
results = collection.query(
    query_texts=["用户查询"],
    n_results=5
)
```

### Pinecone

```python
import pinecone

# 初始化
pinecone.init(api_key="your-api-key", environment="us-west1-gcp")

# 创建索引
index_name = "documents"
if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        name=index_name,
        dimension=384,
        metric="cosine"
    )

# 获取索引
index = pinecone.Index(index_name)

# 上传向量
vectors = [
    {
        "id": str(i),
        "values": embedding.tolist(),
        "metadata": {"text": doc.page_content}
    }
    for i, (embedding, doc) in enumerate(zip(embeddings, documents))
]

index.upsert(vectors=vectors)

# 查询
query_embedding = embedder.encode(["用户查询"])[0].tolist()
results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True
)
```

## RAG框架

### LangChain RAG

```python
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# 创建嵌入模型
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 创建向量存储
vectorstore = FAISS.from_documents(
    documents,
    embeddings
)

# 创建LLM
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

# 创建提示模板
prompt_template = """
基于以下上下文信息回答问题。如果上下文中没有相关信息，请说"我无法从提供的上下文中找到答案"。

上下文:
{context}

问题: {question}

答案:
"""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

# 创建RAG链
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)

# 查询
query = "你的问题"
result = qa_chain({"query": query})

print(f"答案: {result['result']}")
print(f"来源文档: {[doc.metadata for doc in result['source_documents']]}")
```

### LlamaIndex RAG

```python
from llama_index import VectorStoreIndex, ServiceContext, SimpleDirectoryReader
from llama_index.llms import OpenAI
from llama_index.embeddings import OpenAIEmbedding

# 加载文档
documents = SimpleDirectoryReader('data').load_data()

# 创建服务上下文
service_context = ServiceContext.from_defaults(
    llm=OpenAI(model="gpt-3.5-turbo", temperature=0),
    embed_model=OpenAIEmbedding(),
    chunk_size=1000,
    chunk_overlap=200
)

# 创建索引
index = VectorStoreIndex.from_documents(
    documents,
    service_context=service_context
)

# 创建查询引擎
query_engine = index.as_query_engine(
    similarity_top_k=5,
    response_mode="compact"
)

# 查询
response = query_engine.query("你的问题")

print(f"答案: {response.response}")
print(f"来源: {response.source_nodes}")
```

## 高级技术

### 查询优化

#### 查询重写

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# 查询重写提示
rewrite_prompt = PromptTemplate(
    input_variables=["question"],
    template="重写以下问题，使其更清晰和具体：{question}"
)

# 创建重写链
rewrite_chain = LLMChain(
    llm=ChatOpenAI(temperature=0),
    prompt=rewrite_prompt
)

# 重写查询
original_query = "用户查询"
rewritten_query = rewrite_chain.run(original_query)
print(f"重写后: {rewritten_query}")
```

#### 多路查询

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# 生成多个查询
multi_query_prompt = PromptTemplate(
    input_variables=["question"],
    template="""生成3个不同角度的查询来回答以下问题：
{question}

查询1:
查询2:
查询3:"""
)

multi_query_chain = LLMChain(
    llm=ChatOpenAI(temperature=0.7),
    prompt=multi_query_prompt
)

# 生成多个查询
queries = multi_query_chain.run(original_query).split('\n')
queries = [q.strip() for q in queries if q.strip()]

# 对每个查询进行检索
all_results = []
for query in queries:
    results = vectorstore.similarity_search(query, k=2)
    all_results.extend(results)

# 去重
unique_results = list({doc.page_content: doc for doc in all_results}.values())
```

### 重排序

```python
from sentence_transformers import CrossEncoder

# 加载重排序模型
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# 获取初始检索结果
initial_results = vectorstore.similarity_search(query, k=10)

# 重排序
query_doc_pairs = [(query, doc.page_content) for doc in initial_results]
scores = reranker.predict(query_doc_pairs)

# 按分数排序
reranked_results = [
    (doc, score) 
    for doc, score in zip(initial_results, scores)
]
reranked_results.sort(key=lambda x: x[1], reverse=True)

# 获取top-k结果
top_results = [doc for doc, score in reranked_results[:5]]
```

### 知识图谱增强

```python
from langchain.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain

# 连接知识图谱
graph = Neo4jGraph(
    url="bolt://localhost:7687",
    username="neo4j",
    password="password"
)

# 创建图谱QA链
chain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0),
    graph=graph,
    verbose=True
)

# 查询
result = chain.run("查找与AI相关的所有概念")
```

## 性能优化

### 缓存机制

```python
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache

# 设置缓存
set_llm_cache(InMemoryCache())

# 后续查询会使用缓存
result1 = qa_chain({"query": "问题1"})
result2 = qa_chain({"query": "问题1"})  # 从缓存获取
```

### 批处理

```python
# 批量查询
queries = ["问题1", "问题2", "问题3"]

# 批量检索
batch_results = []
for query in queries:
    results = vectorstore.similarity_search(query, k=3)
    batch_results.append(results)

# 批量生成
from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    chain_type="stuff"
)

# 批量处理
batch_answers = []
for query in queries:
    answer = qa_chain.run(query)
    batch_answers.append(answer)
```

## 评估方法

### 检索质量评估

```python
from sklearn.metrics import precision_recall_fscore_support

# 评估检索质量
def evaluate_retrieval(retrieved_docs, relevant_docs, k=5):
    """评估检索质量"""
    retrieved_set = set([doc.metadata['id'] for doc in retrieved_docs[:k]])
    relevant_set = set(relevant_docs)
    
    # 计算指标
    precision = len(retrieved_set & relevant_set) / len(retrieved_set)
    recall = len(retrieved_set & relevant_set) / len(relevant_set)
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    }
```

### 生成质量评估

```python
from evaluate import load

# BLEU评估
bleu = load("bleu")
results = bleu.compute(
    predictions=[generated_answer],
    references=[[reference_answer]]
)

# ROUGE评估
rouge = load("rouge")
results = rouge.compute(
    predictions=[generated_answer],
    references=[[reference_answer]]
)
```

## 最佳实践

### 1. 文档预处理

```python
def preprocess_documents(documents):
    """文档预处理"""
    processed_docs = []
    
    for doc in documents:
        # 清理文本
        text = doc.page_content
        text = text.strip()
        text = ' '.join(text.split())  # 去除多余空格
        
        # 过滤空文档
        if len(text) > 50:
            processed_docs.append({
                'page_content': text,
                'metadata': doc.metadata
            })
    
    return processed_docs
```

### 2. 分块策略选择

```python
# 根据文档类型选择分块策略
def choose_chunking_strategy(document_type):
    strategies = {
        'code': {'chunk_size': 500, 'chunk_overlap': 50},
        'article': {'chunk_size': 1000, 'chunk_overlap': 200},
        'book': {'chunk_size': 1500, 'chunk_overlap': 300},
        'qa': {'chunk_size': 300, 'chunk_overlap': 50}
    }
    
    return strategies.get(document_type, {'chunk_size': 1000, 'chunk_overlap': 200})
```

### 3. 检索参数调优

```python
# 调优检索参数
def tune_retrieval_parameters(vectorstore, query, relevant_docs):
    """调优检索参数"""
    best_k = 3
    best_score = 0
    
    for k in range(1, 11):
        results = vectorstore.similarity_search(query, k=k)
        score = evaluate_retrieval(results, relevant_docs, k=k)['f1']
        
        if score > best_score:
            best_score = score
            best_k = k
    
    return best_k
```

## 常见问题

### Q1: 如何提高检索准确率？

**A**: 优化方法：
- 使用更好的嵌入模型
- 优化分块策略
- 添加重排序
- 使用混合检索

### Q2: 如何处理长文档？

**A**: 处理策略：
- 合理分块
- 层次索引
- 摘要+详情
- 滑动窗口

### Q3: 如何减少幻觉？

**A**: 减少方法：
- 限制生成范围
- 引用来源
- 事实核查
- 温度参数调优

## 参考资料

- [RAG Paper](https://arxiv.org/abs/2005.11401)
- [LangChain Documentation](https://python.langchain.com/)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
