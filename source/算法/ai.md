# AI

## 概念
* langchain
* 微调：Freeze方法、P-Tuning方法和Lora方法
* prompt


## NLP
- 语言模型演进
  - SLM（统计语言模型）
  - NLM（神经网络语言模型）
  - PLM(预训练语言模型)
  - LLM（大模型）
  - PLLM(多模态大模型)

## CV

## 语音识别
## 自动驾驶
## 机器翻译
## 智能问答

## 大模型LLM(开源大型语言模型)
> 社区资料： [Hugging-Face](https://g.126.fm/01WwwzE)
>
> 词向量-Cbow/Skip-Gram
> ![img_2.png](img_2.png)

- ELMo-双向LSTM
- GPT-Transformer(Pre-training + Fine-tuning)
- BERT-Mask Language Model（MLM）/Next Sentence Prediction（NSP）
  ![img.png](img.png)
- Llama2
```bash
#colab执行
%cd /content
!apt-get -y install -qq aria2

!git clone -b v1.8 https://github.com/camenduru/text-generation-webui
%cd /content/text-generation-webui
!pip install -r requirements.txt

!aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/4bit/Llama-2-13b-chat-hf/resolve/main/model-00001-of-00003.safetensors -d /content/text-generation-webui/models/Llama-2-13b-chat-hf -o model-00001-of-00003.safetensors
!aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/4bit/Llama-2-13b-chat-hf/resolve/main/model-00002-of-00003.safetensors -d /content/text-generation-webui/models/Llama-2-13b-chat-hf -o model-00002-of-00003.safetensors
!aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/4bit/Llama-2-13b-chat-hf/resolve/main/model-00003-of-00003.safetensors -d /content/text-generation-webui/models/Llama-2-13b-chat-hf -o model-00003-of-00003.safetensors
!aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/4bit/Llama-2-13b-chat-hf/raw/main/model.safetensors.index.json -d /content/text-generation-webui/models/Llama-2-13b-chat-hf -o model.safetensors.index.json
!aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/4bit/Llama-2-13b-chat-hf/raw/main/special_tokens_map.json -d /content/text-generation-webui/models/Llama-2-13b-chat-hf -o special_tokens_map.json
!aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/4bit/Llama-2-13b-chat-hf/resolve/main/tokenizer.model -d /content/text-generation-webui/models/Llama-2-13b-chat-hf -o tokenizer.model
!aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/4bit/Llama-2-13b-chat-hf/raw/main/tokenizer_config.json -d /content/text-generation-webui/models/Llama-2-13b-chat-hf -o tokenizer_config.json
!aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/4bit/Llama-2-13b-chat-hf/raw/main/config.json -d /content/text-generation-webui/models/Llama-2-13b-chat-hf -o config.json
!aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/4bit/Llama-2-13b-chat-hf/raw/main/generation_config.json -d /content/text-generation-webui/models/Llama-2-13b-chat-hf -o generation_config.json

%cd /content/text-generation-webui
!python server.py --share --chat --load-in-8bit --model /content/text-generation-webui/models/Llama-2-13b-chat-hf
```
- ChatGLM
- vicuna
- 其他 ：
  - UniLM、
  - XLNet、
  - BART、
  - RoBERTa、
  - ERNIE、
  - ALBERT、
  - Electra
  - T5
  - MT-DNN
  - PaLM2


### Stable-Diffusion
生成式模型，文本转图像，
### 开源模型
- 百度-文心一言
- 阿里-通义千问
- 腾讯—混元助手
- 华为—盘古
- 科大讯飞—讯飞星火
- 网易—玉言
- 360—360智脑
- 京东—言犀
- 悟道大模型
### Benchmarks
- SuperGLUE（NLP）
- ImageNet(CV)

## 应用
- Ai办公
- AI图像
- AICode
- AI问答
![img_3.png](img_3.png)
![img_4.png](img_4.png)
## 免费云计算
- colab
- Kaggle
- Paperspace
- SageMaker

## 会议
![img_1.png](img_1.png)
