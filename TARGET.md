# TARGET.md
此文件描述项目需要达成的目标
# 概述
使用云端LLM，本地部署于LM studio的Coder LLM和Embedding构建MultiAgents coder。
使用LangChain和DeepAgent构建工作流

# 可用资源
云端LLM：配置于env.json
本地LM studio:omni-coder-9B,Qwen3-embedding-0.6B,Qwen3.5-4B

# 工作流概述
1.使用MinerU分析文档，保存于StateBackend
2.交由云端LLM处理，分解为多层任务，分解程度应精确到需要完成的函数，附带的参数表，输出类型
3.任务保存于deepagents的todo list,载入omni-coder-9B,由omni-coder-9B逐个完成编写
4.若todo list过长，先将任务保存于Filesystembackend,之后逐步载入todo list
5.unload omni-coder-9B
6.云端LLM将所有代码整合为可执行代码
7.测试代码并纠错，纠错流程遵循步骤2-5
8.载入omni-coder-9B对所有类、函数编写注释
9.unload omni-coder-9B
10.载入Qwen3-embedding-0.6B，对所有注释和函数名进行嵌入编码，保存于Filesystembackend（需与步骤4的分离）

# 工作流细则
1.由于显存资源受限，本地部署的模型需要互斥载入，构建ModelManager保持omni-coder-9B不与其他本地模型同时载入
2.由于MinerU未调试完成，暂时使用占位符
3.DeepAgent和LangGraph是LangChain的衍生，具体可见deepagents skill和langchain skill