# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LangAgent is a multi AI agent project for coding assist that integrates multiple LLM backends:
- **MiniMax** (cloud) - configured via `env.json`
- **LM Studio** (local) - for running GGUF models locally
- **deepagents** framework - for building agents with tool calling, file system access, human-in-the-loop, and subagent delegation

## Common Commands

### Running the chatbot agent
```bash
python main.py
```
Uses `deepagents` with `FilesystemBackend` and `MemorySaver` for conversation persistence. Reads config from `env.json`.

### Testing local LM Studio inference
```bash
python Local_example.py
python useLM.py
```

### Document extraction with MinerU
```bash
mineru-open-api flash-extract <file>     # Quick extract (no token, 10MB/20页 limit)
mineru-open-api extract <file>           # Precision extract (requires auth)
```

### Virtual environment
```powershell
.\venv\Scripts\activate  # Activate venv on Windows
pip install <package>      # Install dependencies
```

## Architecture

### Entry Points
- `main.py` - Chatbot using `create_deep_agent()` with filesystem tools and conversation checkpointing
- `Local_example.py` / `useLM.py` - LM Studio local inference examples

### Configuration
- `env.json` - API keys and model configs for backends (MINIMAX, LOCAL)

### Dependencies
- `deepagents` - Agent framework (langchain-doc based)
- `langgraph` - Checkpointing/state management
- `lmstudio` - Local GGUF model inference
- `langchain-anthropic` - Anthropic LLM integration

## Code Style
- PEP8 compliance
- Function length ≤40 lines (split if larger)
- Import order: stdlib → third-party → local modules

## Key Patterns

### Creating an agent with filesystem backend
```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    model=llm,
    tools=[...],
    backend=FilesystemBackend(root_dir="."),
    checkpointer=MemorySaver()
)
```

### Local LLM with LM Studio
```python
import lmstudio as lms
model = lms.llm("qwen3.5-4B")
result = model.respond("prompt")
```

## LLM Configuration

### MiniMax (云端 - 编排者)
- **用途**: 任务分解、代码整合、测试纠错
- **Context Window**: 需查阅API文档
- **Temperature**: 0.7-0.8 (平衡创造性和一致性)
- **推荐Prompt模板**:
  ```
  你是一个专业的代码架构师。用户提供一份需求文档，请将其分解为具体的函数实现任务。
  每个任务需要包含：函数名、参数列表、返回值类型、功能描述。
  输出格式为JSON数组。
  ```

### omni-coder-9B (本地 - 代码执行)
- **Context Limit**: 16384 tokens (重要：切勿超过)
- **GPU Offload**: 建议配置 `gpu: { ratio: 0.5 }`
- **Temperature**: 0.2-0.3 (代码生成需要精确)
- **推荐Prompt模板**:
  ```
  任务：{description}
  函数名：{function_name}
  参数类型：{parameters}
  返回类型：{output_type}

  请编写完整的Python函数实现。保持简洁，遵循PEP8。
  ```
- **注意事项**: 单次输入token必须控制在16384以内

### Qwen3-embedding-0.6B (本地 - 嵌入编码)
- **用途**: 代码片段嵌入存储
- **Context Limit**: 需查阅模型文档
- **推荐用途**: 函数名、注释、代码片段的语义嵌入

## Testing Workflow

### 单模块测试流程
1. 每个模块创建独立测试文件 `test_<module>.py`
2. 测试通过后提交: `git add . && git commit -m "feat: add <module> - tests passing"`
3. 集成到主模块后再提交一次

### Git 提交规范
```bash
git add <changed_files>
git commit -m "feat: add <description>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```
