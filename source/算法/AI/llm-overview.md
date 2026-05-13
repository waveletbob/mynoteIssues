# 大语言模型 (LLM) 技术详解

## Transformer 核心机制

LLM 基于 Transformer 的 Decoder-only 架构，核心是自注意力机制：

```
输入 Token → Embedding + 位置编码 → N×Transformer Block → LM Head → 输出概率分布
```

**关键技术演进**：

| 机制 | 作用 | 代表 |
|------|------|------|
| Multi-Head Attention | 多头并行关注不同位置 | 原始 Transformer |
| FlashAttention | IO 感知加速，显存优化 | vLLM、FlashAttention-2 |
| GQA (Grouped Query) | 共享 KV 头，减少缓存 | Llama 2+、Mistral |
| RoPE | 旋转位置编码，相对位置 | Llama、Qwen、DeepSeek |
| MoE | 稀疏专家，扩大容量不增算力 | Mixtral、DeepSeek-V3 |

## 预训练范式

| 范式 | 方法 | 代表模型 |
|------|------|----------|
| **MLM** (Masked LM) | 随机 mask，双向预测 | BERT、RoBERTa |
| **CLM** (Causal LM) | 自回归预测下一个 token | GPT、Llama |
| **Seq2Seq** | Encoder-Decoder 结构 | T5、BART |

现代主流 LLM 均为 **CLM (Decoder-only)** 架构。

## 微调方法

```
Full Fine-tuning (全参)     → 效果最好，成本最高
LoRA (低秩适配)              → 只训练小矩阵，消费级 GPU 可行
QLoRA (量化 LoRA)            → 4-bit 量化 + LoRA，更低显存
DPO (直接偏好优化)           → 替代 RLHF，更稳定
```

### LoRA 核心代码

```python
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=8,                          # 秩：越大越接近全参，通常 8-64
    lora_alpha=32,                # 缩放因子
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
)
model = get_peft_model(base_model, lora_config)
model.print_trainable_parameters()  # 通常 < 1% 参数
```

## 推理优化

| 技术 | 原理 | 工具 |
|------|------|------|
| **量化** | INT8/INT4 降低精度，减显存 | GPTQ、AWQ、bitsandbytes |
| **PagedAttention** | 分页管理 KV cache | vLLM |
| **投机解码** | 小模型草稿，大模型校验 | llama.cpp、Medusa |
| **连续批处理** | 动态合并请求 | vLLM、TensorRT-LLM |

## 常用评估基准

| 基准 | 测什么 | 说明 |
|------|--------|------|
| MMLU | 综合知识 | 57 学科多选题 |
| HumanEval | 代码生成 | 164 道 Python 题 |
| GSM8K | 数学推理 | 小学数学应用题 |
| MATH | 高等数学 | 竞赛级别数学 |
| SWE-bench | 软件工程 | 真实 GitHub Issue 修复 |

---

*最后更新: 2026年5月*
