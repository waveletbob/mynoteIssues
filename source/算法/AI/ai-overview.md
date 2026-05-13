# AI 人工智能技术全景

AI 技术领域快速索引，各专题详情见对应文档。

## 发展脉络

```
1950s 图灵测试 → 1980s 专家系统 → 1990s 统计学习
→ 2006 深度学习 → 2012 AlexNet/CNN → 2017 Transformer
→ 2018 BERT/GPT → 2022 ChatGPT → 2023 多模态爆发
→ 2024 AI Agent + MCP/SKILL 工程化 → 2025 持续演进
```

## 核心技术栈

| 领域 | 关键技术 | 详见 |
|------|---------|------|
| **LLM** | Transformer、预训练、微调(LoRA/QLoRA)、RLHF/DPO | [llm-overview](llm-overview) |
| **RAG** | 向量检索、文档分块、重排序、知识图谱 | [rag-technology](rag-technology) |
| **Agent** | 感知-规划-行动-学习循环、工具调用、多Agent协作 | [ai-agent](ai-agent) |
| **多模态** | CLIP、Stable Diffusion、GPT-4V、视觉语言模型 | [multimodal-ai](multimodal-ai) |
| **MCP** | 工具协议、资源管理、安全认证 | [mcp-technology](mcp-technology) |
| **SKILL** | 技能定义、技能组合、技能评估 | [skill-system](skill-system) |

## 主流模型速查

### 闭源（API 调用）

| 模型 | 厂商 | 核心优势 |
|------|------|----------|
| GPT-4o | OpenAI | 多模态原生，实时语音 |
| Claude 3.5 Sonnet | Anthropic | 编程最强，200K 上下文 |
| Gemini 2.5 Pro | Google | 超长上下文 1M+，推理强 |
| Kimi | 月之暗面 | 200 万超长文本 |

### 开源（本地部署）

| 模型 | 参数 | 核心优势 |
|------|------|----------|
| Llama 3/4 | 8B-405B | Meta 开源标杆 |
| Qwen2.5/3 | 0.5B-72B | 阿里，中文最强 |
| DeepSeek-V3/R1 | 67B | MoE 架构，编程/推理顶尖 |
| Mistral Large | 123B | 欧洲最强，多语言 |
| Gemma 3 | 1B-27B | Google，轻量高效 |

## 模型训练管线

```
数据准备 → 预训练 → SFT 微调 → RLHF/DPO 对齐 → 评估 → 部署
```

关键方法：
- **全参微调**：效果最好，硬件成本高
- **LoRA/QLoRA**：低秩适配，消费级 GPU 可用
- **DPO**：直接偏好优化，比 RLHF 更稳定

## 推理部署方案

| 方案 | 适用场景 | 工具 |
|------|---------|------|
| 云端 API | 快速接入 | OpenAI、Azure、阿里百炼 |
| 本地推理 | 数据隐私、低成本 | Ollama、vLLM、llama.cpp |
| 混合部署 | 弹性伸缩 | K8s + GPU 集群 |

## 评估基准

| 维度 | 代表性基准 |
|------|-----------|
| 综合理解 | MMLU、C-Eval |
| 代码能力 | HumanEval、MBPP、SWE-bench |
| 数学推理 | GSM8K、MATH |
| 中文能力 | CMMLU、C-Eval |

## 学习路径

1. **入门**：了解 LLM 基本概念 → 学会写 prompt
2. **应用**：搭建 RAG 系统 → 调用 Agent 框架
3. **进阶**：微调模型(LoRA) → 搭建 MCP Server → 设计 SKILL
4. **工程化**：本地部署(vLLM/Ollama) → 性能调优 → 生产运维

## 文档索引

- [ai-practice-summary](ai-practice-summary) - AI 编程助手五大核心能力实践总结
- [llm-overview](llm-overview) - 大语言模型技术详解
- [rag-technology](rag-technology) - 检索增强生成技术
- [ai-agent](ai-agent) - AI 智能体开发
- [multimodal-ai](multimodal-ai) - 多模态 AI 技术
- [mcp-technology](mcp-technology) - MCP 模型上下文协议
- [skill-system](skill-system) - AI 技能系统
- [prompt-engineering](prompt-engineering) - 提示工程
- [model-training](model-training) - 模型训练指南
- [model-deployment](model-deployment) - 模型部署指南
- [ai-applications](ai-applications) - AI 应用场景

---

*最后更新: 2026年5月*