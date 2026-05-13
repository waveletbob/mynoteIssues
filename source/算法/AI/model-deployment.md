# 模型部署指南

## 部署方案对比

| 方案 | 延迟 | 成本 | 隐私 | 工具 |
|------|------|------|------|------|
| 云端 API | 低（网络） | 按量付费 | 低 | OpenAI、Azure、阿里百炼 |
| 本地 Ollama | 取决于硬件 | 硬件投入 | 高 | Ollama + llama.cpp |
| vLLM 服务 | 极低 | GPU 成本 | 高 | vLLM、SGLang |
| 混合部署 | 灵活 | 弹性 | 可控 | K8s + GPU 调度 |

## 本地部署三步走

### 1. 用 Ollama 快速验证

```bash
ollama pull qwen2.5:7b    # 下载模型
ollama run qwen2.5:7b     # 命令行测试
ollama serve               # 启动 API 服务（端口 11434）
```

### 2. 用 vLLM 生产部署

```bash
pip install vllm
vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000
```

关键参数：`--max-model-len 8192` `--gpu-memory-utilization 0.9`

### 3. 容器化

```dockerfile
FROM vllm/vllm-openai:latest
ENV MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
CMD ["--port", "8000"]
```

## 性能调优

| 优化方向 | 方法 | 效果 |
|---------|------|------|
| 减少显存 | INT4 量化 (AWQ/GPTQ) | 显存降 75% |
| 提升吞吐 | 连续批处理 | 吞吐 10x |
| 降低首字延迟 | 投机解码 | 延迟降 2-3x |
| 长文本加速 | FlashAttention | O(n²) → O(n) 显存 |

## 监控要点

- **GPU 利用率**：目标 > 80%
- **请求延迟**：P50/P99，设置告警阈值
- **Token 速率**：tokens/s，衡量实际吞吐
- **错误率**：OOM、超时、模型崩溃

---

*最后更新: 2026年5月*
