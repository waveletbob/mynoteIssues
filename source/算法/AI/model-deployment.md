# 模型部署指南

## 部署概述

模型部署是将训练好的模型集成到生产环境中的过程，包括模型优化、服务部署、监控维护等环节。

## 部署方式

### 云端部署

#### OpenAI API

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

#### Azure OpenAI

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="your-api-key",
    api_version="2024-02-01",
    azure_endpoint="https://your-resource.openai.azure.com"
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### 本地部署

#### Ollama

```bash
# 安装Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型
ollama pull llama2

# 运行模型
ollama run llama2

# API服务
ollama serve
```

```python
import requests

# 调用Ollama API
response = requests.post('http://localhost:11434/api/generate', json={
    'model': 'llama2',
    'prompt': 'Hello, how are you?',
    'stream': False
})

print(response.json()['response'])
```

#### vLLM

```python
from vllm import LLM, SamplingParams

# 初始化LLM
llm = LLM(model="meta-llama/Llama-2-7b-hf")

# 配置采样参数
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.95,
    max_tokens=100
)

# 生成文本
prompts = ["Hello, my name is"]
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(f"Prompt: {output.prompt}")
    print(f"Generated: {output.outputs[0].text}\n")
```

## 性能优化

### 模型量化

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

# 量化配置
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# 加载量化模型
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto"
)
```

### 推理加速

```python
# 使用Flash Attention
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    attn_implementation="flash_attention_2",
    torch_dtype=torch.float16,
    device_map="auto"
)
```

### 批处理

```python
# 批量推理
def batch_inference(model, tokenizer, prompts, batch_size=8):
    """批量推理"""
    results = []
    
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i + batch_size]
        inputs = tokenizer(batch, return_tensors="pt", padding=True)
        
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=100)
        
        for output in outputs:
            result = tokenizer.decode(output, skip_special_tokens=True)
            results.append(result)
    
    return results
```

## 服务部署

### FastAPI服务

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

app = FastAPI()

# 加载模型
model = AutoModelForCausalLM.from_pretrained("model-path")
tokenizer = AutoTokenizer.from_pretrained("model-path")

class GenerationRequest(BaseModel):
    prompt: str
    max_length: int = 100
    temperature: float = 0.7

@app.post("/generate")
async def generate(request: GenerationRequest):
    """生成文本"""
    try:
        inputs = tokenizer(request.prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=request.max_length,
                temperature=request.temperature
            )
        
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {"result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Docker部署

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  model-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL_PATH=/models/llama-2-7b
    volumes:
      - ./models:/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## 监控和日志

### 性能监控

```python
from prometheus_client import Counter, Histogram, start_http_server

# 定义指标
request_count = Counter('model_requests_total', 'Total model requests')
request_duration = Histogram('model_request_duration_seconds', 'Request duration')

@app.post("/generate")
@request_duration.time()
async def generate(request: GenerationRequest):
    request_count.inc()
    # 生成逻辑
    pass

# 启动监控服务
start_http_server(8001)
```

### 日志记录

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.post("/generate")
async def generate(request: GenerationRequest):
    logger.info(f"Received request: {request.prompt}")
    
    try:
        result = model.generate(request)
        logger.info(f"Generated response: {result[:100]}...")
        return {"result": result}
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise
```

## 安全考虑

### 输入验证

```python
from pydantic import validator

class GenerationRequest(BaseModel):
    prompt: str
    max_length: int = 100
    temperature: float = 0.7
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if len(v) > 10000:
            raise ValueError("Prompt too long")
        # 检查恶意内容
        if contains_malicious_content(v):
            raise ValueError("Malicious content detected")
        return v
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        return v
```

### 速率限制

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/generate")
@limiter.limit("10/minute")
async def generate(request: GenerationRequest):
    # 生成逻辑
    pass
```

## 最佳实践

### 1. 模型版本管理

```python
# 使用模型版本控制
MODEL_VERSIONS = {
    "v1.0": "model-path-v1.0",
    "v1.1": "model-path-v1.1",
    "v2.0": "model-path-v2.0"
}

def load_model(version="latest"):
    """加载指定版本的模型"""
    if version == "latest":
        version = max(MODEL_VERSIONS.keys())
    
    model_path = MODEL_VERSIONS[version]
    return AutoModelForCausalLM.from_pretrained(model_path)
```

### 2. 错误处理

```python
@app.post("/generate")
async def generate(request: GenerationRequest):
    try:
        # 验证输入
        validate_input(request)
        
        # 生成文本
        result = model.generate(request)
        
        # 验证输出
        validate_output(result)
        
        return {"result": result}
    
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except ModelError as e:
        logger.error(f"Model error: {str(e)}")
        raise HTTPException(status_code=500, detail="Model error")
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 3. 资源管理

```python
# GPU内存管理
def clear_gpu_memory():
    """清理GPU内存"""
    torch.cuda.empty_cache()
    gc.collect()

# 模型卸载
def unload_model(model):
    """卸载模型"""
    del model
    clear_gpu_memory()
```

## 常见问题

### Q1: 如何选择部署方式？

**A**: 考虑因素：
- 成本预算
- 性能要求
- 数据隐私
- 维护复杂度

### Q2: 如何优化推理速度？

**A**: 优化方法：
- 模型量化
- 批处理
- 缓存机制
- 硬件加速

### Q3: 如何保证服务稳定性？

**A**: 稳定性措施：
- 负载均衡
- 自动扩缩容
- 健康检查
- 故障恢复
