# 大语言模型 (LLM) 技术详解

## LLM概述

大语言模型（Large Language Model，LLM）是当前AI领域最重要的技术突破之一。它们通过在海量文本数据上进行预训练，学习到了丰富的语言知识和推理能力。

## 核心技术

### Transformer架构

Transformer是现代LLM的基础架构，其核心创新是自注意力机制（Self-Attention）。

```python
import torch
import torch.nn as nn

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)
        
        # Linear projections
        Q = self.W_q(query)
        K = self.W_k(key)
        V = self.W_v(value)
        
        # Reshape for multi-head attention
        Q = Q.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / torch.sqrt(torch.tensor(self.d_k, dtype=torch.float32))
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attention_weights = torch.softmax(scores, dim=-1)
        output = torch.matmul(attention_weights, V)
        
        # Reshape back
        output = output.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        
        return self.W_o(output)
```

### 预训练范式

#### 1. 掩码语言模型 (MLM)

BERT使用MLM预训练方法，随机mask输入token，让模型预测被mask的token。

```python
def masked_language_model_loss(model, input_ids, attention_mask, mlm_mask, labels):
    """
    计算MLM损失
    """
    # 前向传播
    outputs = model(input_ids=input_ids, 
                    attention_mask=attention_mask,
                    labels=labels)
    
    # 获取loss
    loss = outputs.loss
    
    return loss
```

#### 2. 因果语言模型 (CLM)

GPT使用CLM预训练方法，预测下一个token。

```python
def causal_language_model_loss(model, input_ids, attention_mask):
    """
    计算CLM损失
    """
    # 前向传播
    outputs = model(input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=input_ids)
    
    # 获取loss
    loss = outputs.loss
    
    return loss
```

## 主流LLM模型

### Llama系列

Llama是Meta开源的LLM系列，具有优秀的性能和开放性。

```python
from transformers import LlamaForCausalLM, LlamaTokenizer

# 加载模型和tokenizer
model = LlamaForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = LlamaTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

# 生成文本
input_text = "The future of AI is"
input_ids = tokenizer.encode(input_text, return_tensors="pt")

with torch.no_grad():
    output = model.generate(input_ids, max_length=100, temperature=0.7)

generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
print(generated_text)
```

### Mistral系列

Mistral AI推出的开源模型，性能优异且效率高。

```python
from transformers import MistralForCausalLM, MistralTokenizer

model = MistralForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
tokenizer = MistralTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")

# 使用方法与Llama类似
```

### Qwen系列

阿里推出的开源模型，中文能力强。

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-7B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-7B")
```

## 模型微调

### LoRA微调

LoRA（Low-Rank Adaptation）是一种高效的参数微调方法。

```python
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM

# 加载基础模型
base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")

# 配置LoRA
lora_config = LoraConfig(
    r=8,  # rank
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# 应用LoRA
model = get_peft_model(base_model, lora_config)

# 查看可训练参数
model.print_trainable_parameters()
```

### QLoRA微调

QLoRA是量化版的LoRA，进一步降低内存需求。

```python
from transformers import BitsAndBytesConfig
from peft import LoraConfig, get_peft_model

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

# 应用LoRA
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
```

## 推理优化

### vLLM推理加速

vLLM使用PagedAttention技术加速推理。

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
prompts = ["Write a story about AI", "Explain quantum computing"]
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(f"Prompt: {output.prompt}")
    print(f"Generated: {output.outputs[0].text}\n")
```

### 量化推理

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# 加载量化模型
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    load_in_8bit=True,
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

# 推理
input_text = "Hello, how are you?"
input_ids = tokenizer.encode(input_text, return_tensors="pt")

with torch.no_grad():
    output = model.generate(input_ids, max_length=50)

generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
print(generated_text)
```

## 评估方法

### 自动评估

```python
from evaluate import load

# BLEU评估
bleu = load("bleu")
predictions = ["the cat is on the mat", "there is a cat on the mat"]
references = [["the cat is on the mat"], ["a cat is on the mat"]]
results = bleu.compute(predictions=predictions, references=references)
print(results)

# ROUGE评估
rouge = load("rouge")
results = rouge.compute(predictions=predictions, references=references)
print(results)
```

### 人工评估

人工评估通常关注以下维度：

- **准确性**: 回答是否正确
- **相关性**: 回答是否相关
- **流畅性**: 语言是否自然
- **完整性**: 回答是否完整
- **安全性**: 是否包含有害内容

## 最佳实践

### 1. 模型选择

根据任务需求选择合适的模型：

- **简单任务**: 7B参数模型足够
- **复杂任务**: 考虑13B或更大模型
- **中文任务**: 优先选择中文优化模型
- **代码任务**: 选择代码专精模型

### 2. 提示工程

精心设计提示词可以显著提升模型性能：

```python
prompt = """
你是一位专业的Python开发工程师。请帮我完成以下任务：

任务：优化以下代码的性能

代码：
{code}

要求：
1. 保持功能不变
2. 提高执行效率
3. 添加必要的注释
4. 说明优化思路

请直接给出优化后的代码。
"""
```

### 3. 上下文管理

合理管理上下文窗口：

```python
# 限制输入长度
max_input_length = 2048
input_ids = tokenizer.encode(input_text, return_tensors="pt", truncation=True, max_length=max_input_length)

# 滑动窗口处理长文本
def process_long_text(text, window_size=1024, overlap=128):
    chunks = []
    for i in range(0, len(text), window_size - overlap):
        chunk = text[i:i + window_size]
        chunks.append(chunk)
    return chunks
```

### 4. 错误处理

```python
def safe_generate(model, tokenizer, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            input_ids = tokenizer.encode(prompt, return_tensors="pt")
            output = model.generate(input_ids, max_length=100)
            return tokenizer.decode(output[0], skip_special_tokens=True)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Attempt {attempt + 1} failed, retrying...")
    return None
```

## 常见问题

### Q1: 如何选择合适的模型大小？

**A**: 考虑以下因素：
- 任务复杂度
- 可用计算资源
- 延迟要求
- 成本预算

### Q2: 如何处理长文本？

**A**: 使用以下策略：
- 滑动窗口
- 分段处理
- 摘要+详情
- 选择支持长上下文的模型

### Q3: 如何提高推理速度？

**A**: 优化方法：
- 使用vLLM等推理框架
- 模型量化
- 批处理
- 缓存机制

## 参考资料

- [Llama 2 Paper](https://arxiv.org/abs/2307.09288)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [QLoRA Paper](https://arxiv.org/abs/2305.14314)
- [vLLM Paper](https://arxiv.org/abs/2309.06180)
