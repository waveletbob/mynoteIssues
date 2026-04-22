# 提示工程 (Prompt Engineering)

## 提示工程概述

提示工程是通过设计和优化输入提示词来引导大语言模型生成期望输出的技术。它是提高AI模型性能和可控性的重要方法。

## 基础技巧

### 1. 清晰指令

提供明确、具体的指令。

```markdown
❌ 坏例子:
写一篇文章

✅ 好例子:
写一篇关于人工智能发展历史的1000字文章，包括以下内容：
1. 关键里程碑事件
2. 重要技术突破
3. 未来发展趋势
4. 对社会的影响
```

### 2. 提供示例

通过示例帮助模型理解任务。

```markdown
任务: 情感分析

示例1:
输入: "这个产品太棒了！"
输出: 正面

示例2:
输入: "服务态度很差，不推荐"
输出: 负面

示例3:
输入: "还可以吧"
输出: 中性

输入: "这个功能很实用"
输出:
```

### 3. 角色设定

为模型设定特定角色。

```markdown
你是一位经验丰富的Python开发工程师，擅长性能优化。
请帮我优化以下代码，提高执行效率。

代码:
{code}

要求:
1. 保持功能不变
2. 提高执行速度
3. 添加必要的注释
4. 说明优化思路
```

### 4. 格式要求

明确指定输出格式。

```markdown
请以JSON格式返回以下信息：
{
  "name": "产品名称",
  "price": "价格",
  "description": "产品描述",
  "features": ["特性1", "特性2"]
}
```

## 高级技巧

### 思维链 (Chain of Thought)

引导模型逐步思考。

```markdown
问题: 如果我有3个苹果，吃了1个，又买了2个，现在有几个苹果？

请一步步思考：
1. 初始有3个苹果
2. 吃了1个，剩下 3-1=2个
3. 又买了2个，变成 2+2=4个
4. 所以现在有4个苹果

答案: 4个
```

### 自我反思

让模型检查和改进自己的答案。

```markdown
请先思考这个问题的解决方案，然后：
1. 检查是否有错误
2. 考虑是否有更好的方法
3. 验证结果的正确性
4. 给出最终答案和改进建议

问题: {question}
```

### 少样本学习 (Few-shot Learning)

提供少量示例让模型学习。

```markdown
任务: 翻译英文到中文

示例1:
Hello -> 你好

示例2:
Good morning -> 早上好

示例3:
How are you? -> 你好吗？

示例4:
Nice to meet you -> 很高兴见到你

输入: Thank you very much
输出:
```

### 思维树 (Tree of Thoughts)

生成多个可能的解决方案并选择最佳方案。

```markdown
对于以下问题，请生成3个不同的解决方案，然后评估每个方案，选择最佳方案。

问题: 如何提高机器学习模型的准确率？

解决方案1:
[方案1内容]

解决方案2:
[方案2内容]

解决方案3:
[方案3内容]

评估和选择:
[评估过程和最终选择]
```

## 提示模板

### 结构化提示

```markdown
# 角色设定
你是一位{role}，擅长{expertise}。

# 任务描述
{task_description}

# 输入信息
{input_information}

# 要求
1. {requirement1}
2. {requirement2}
3. {requirement3}

# 输出格式
{output_format}

# 示例
{example}

# 现在请处理以下输入
{current_input}
```

### 任务分解提示

```markdown
# 主任务
{main_task}

# 任务分解
请将主任务分解为以下子任务：

1. 子任务1: {subtask1}
   - 具体要求: {requirements1}
   - 预期输出: {expected_output1}

2. 子任务2: {subtask2}
   - 具体要求: {requirements2}
   - 预期输出: {expected_output2}

3. 子任务3: {subtask3}
   - 具体要求: {requirements3}
   - 预期输出: {expected_output3}

# 执行顺序
{execution_order}

# 最终整合
请将各子任务的结果整合成最终答案。
```

### 迭代优化提示

```markdown
# 初始方案
{initial_solution}

# 优化要求
请从以下方面优化初始方案：
1. 准确性: 检查是否有错误
2. 完整性: 是否遗漏重要内容
3. 清晰性: 表达是否清晰易懂
4. 效率性: 是否有更高效的方法

# 优化过程
请逐步说明优化过程：
1. 发现的问题
2. 改进的方法
3. 优化后的结果

# 最终方案
{optimized_solution}
```

## 应用场景

### 1. 代码生成

```markdown
你是一位专业的{language}开发工程师。

任务: 编写一个{function_type}函数

功能描述:
{function_description}

输入参数:
- {param1}: {param1_description}
- {param2}: {param2_description}

输出:
{output_description}

要求:
1. 代码要清晰易读
2. 添加必要的注释
3. 包含错误处理
4. 提供使用示例

请直接给出代码实现。
```

### 2. 文本摘要

```markdown
任务: 对以下文本进行摘要

原文:
{original_text}

摘要要求:
1. 保留关键信息
2. 语言简洁明了
3. 字数控制在{word_count}字以内
4. 保持原文的逻辑结构

摘要:
```

### 3. 问答系统

```markdown
# 上下文信息
{context}

# 问题
{question}

# 回答要求
1. 基于上下文信息回答
2. 如果上下文中没有相关信息，请明确说明
3. 回答要准确、完整
4. 引用相关的上下文内容

# 回答
```

### 4. 数据分析

```markdown
你是一位数据分析师。

# 数据描述
{data_description}

# 分析任务
{analysis_task}

# 分析要求
1. 使用Python进行数据分析
2. 包含数据可视化
3. 提供详细的分析结论
4. 给出可行的建议

# 分析步骤
1. 数据加载和预处理
2. 探索性数据分析
3. 深度分析
4. 结论和建议

请开始分析。
```

## 优化策略

### 1. 提示词调优

```python
def optimize_prompt(initial_prompt, task, examples):
    """优化提示词"""
    
    # 添加角色设定
    optimized_prompt = f"""
你是一位专业的{task}专家。
    
{initial_prompt}
"""
    
    # 添加示例
    if examples:
        optimized_prompt += "\n\n示例:\n"
        for i, example in enumerate(examples, 1):
            optimized_prompt += f"示例{i}:\n{example}\n"
    
    # 添加要求
    optimized_prompt += """
要求:
1. 回答要准确、完整
2. 语言要清晰、简洁
3. 格式要规范、统一
"""
    
    return optimized_prompt
```

### 2. 迭代改进

```python
def iterative_improvement(prompt, model, max_iterations=3):
    """迭代改进提示词"""
    
    current_prompt = prompt
    for i in range(max_iterations):
        # 生成回答
        response = model.generate(current_prompt)
        
        # 评估回答质量
        quality_score = evaluate_quality(response)
        
        # 如果质量足够好，停止迭代
        if quality_score >= 0.8:
            break
        
        # 改进提示词
        current_prompt = improve_prompt(current_prompt, response)
    
    return current_prompt, response
```

### 3. A/B测试

```python
def ab_test_prompts(prompt_a, prompt_b, model, test_cases):
    """A/B测试提示词"""
    
    results_a = []
    results_b = []
    
    for test_case in test_cases:
        # 测试提示词A
        response_a = model.generate(prompt_a.format(**test_case))
        score_a = evaluate_response(response_a, test_case)
        results_a.append(score_a)
        
        # 测试提示词B
        response_b = model.generate(prompt_b.format(**test_case))
        score_b = evaluate_response(response_b, test_case)
        results_b.append(score_b)
    
    # 比较结果
    avg_score_a = sum(results_a) / len(results_a)
    avg_score_b = sum(results_b) / len(results_b)
    
    if avg_score_a > avg_score_b:
        return prompt_a, avg_score_a
    else:
        return prompt_b, avg_score_b
```

## 常见问题

### Q1: 如何处理长文本？

**A**: 处理策略：
- 分段处理
- 摘要+详情
- 滑动窗口
- 层次化处理

### Q2: 如何提高回答的准确性？

**A**: 提高方法：
- 提供更多上下文
- 使用思维链
- 添加示例
- 明确要求

### Q3: 如何避免模型幻觉？

**A**: 避免方法：
- 限制生成范围
- 要求引用来源
- 使用RAG
- 事实核查

## 最佳实践

### 1. 提示词设计原则

- **清晰性**: 指令要明确具体
- **完整性**: 包含所有必要信息
- **一致性**: 格式和风格保持一致
- **简洁性**: 避免冗余信息

### 2. 错误处理

```python
def safe_prompt_execution(model, prompt, max_retries=3):
    """安全执行提示"""
    
    for attempt in range(max_retries):
        try:
            response = model.generate(prompt)
            
            # 验证响应质量
            if validate_response(response):
                return response
            
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"尝试 {attempt + 1} 失败，重试...")
    
    return None
```

### 3. 提示词管理

```python
class PromptManager:
    """提示词管理器"""
    
    def __init__(self):
        self.prompts = {}
    
    def add_prompt(self, name, prompt):
        """添加提示词"""
        self.prompts[name] = prompt
    
    def get_prompt(self, name, **kwargs):
        """获取提示词"""
        prompt = self.prompts.get(name)
        if prompt:
            return prompt.format(**kwargs)
        return None
    
    def update_prompt(self, name, new_prompt):
        """更新提示词"""
        self.prompts[name] = new_prompt
```

## 参考资料

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Library](https://docs.anthropic.com/claude/prompt-library)
- [LangChain Prompt Templates](https://python.langchain.com/docs/modules/prompts/)
