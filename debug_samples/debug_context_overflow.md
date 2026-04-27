# Omni-coder-9B 上下文超限问题分析

## 问题描述
运行 main_multiagent.py 时，step8（omni-coder写注释）出现超长输出（25904字符），包含大量 "Thinking Process" 内容。

## 可能原因

### 1. 模型配置未生效
- **症状**：temperature/top_p/top_k 配置可能未正确传递给 LM Studio
- **检查点**：`ModelConfig.to_lms_config()` 是否正确？`lms.llm(name, config=)` 是否正确接收？
- **验证方式**：打印 model.get_load_config() 查看实际配置

### 2. 模型会话累积历史
- **症状**：连续调用 respond() 时，上下文可能累积
- **检查点**：`lms.llm()` 返回的是否是同一个模型实例？实例是否维持历史？
- **验证方式**：连续3次调用相同 prompt，观察输出长度变化

### 3. Prompt 模板过长
- **症状**：_step8 的 OMNI_CODER_PROMPT_COMMENT 包含完整代码 + 系统指令
- **检查点**：当代码很长时，prompt 可能会触发模型的详细思考模式
- **验证方式**：减少代码量测试

### 4. 模型本身的 Thinking Process 特性
- **症状**：omni-coder-9B 默认可能开启 Thinking Process 输出
- **检查点**：某些 GGUF 模型有内置的 thought/chain-of-thought 机制
- **验证方式**：查看模型说明文档，或尝试其他模型

### 5. temperature 设置过高
- **症状**：temperature=0.3 仍然产生长输出
- **检查点**：配置中 temperature 是否真的生效？
- **验证方式**：设置极低 temperature (如 0.1) 或极高 (0.9) 观察差异

### 6. top_p/top_k 未生效
- **症状**：采样参数可能未正确传递
- **检查点**：LM Studio SDK 的 config 参数格式是否正确？
- **验证方式**：查看 lms.llm() 的 config 参数文档

### 7. 模型加载时的配置优先级
- **症状**：LM Studio 客户端可能有默认配置覆盖代码中的设置
- **检查点**：LM Studio APP 中是否设置了模型默认参数？
- **验证方式**：在 LM Studio APP 中检查/重置模型默认参数

## 已验证的情况
- 连续3次调用 respond()，输出长度约 750-950 字符（无累积）
- 配置传递方式：`lms.llm(model_name, config={"temperature": 0.3, ...})`

## 待验证项
1. 检查 `ModelConfig.to_lms_config()` 返回值
2. 检查 `lms.llm()` 是否正确接收 config
3. 在 LM Studio APP 中确认模型参数设置
4. 尝试在 config 中添加 `enable_thinking: false` 或类似选项