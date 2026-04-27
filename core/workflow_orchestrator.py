import json
import pickle

from langchain_anthropic import ChatAnthropic

from core.model_manager import ModelManager
from core.task_schema import Task, CodeResult, WorkflowResult
from core.embedding_pipeline import EmbeddingPipeline
from deepagents.backends import FilesystemBackend


class WorkflowOrchestrator:
    """多智能体编码工作流编排器

    管理10步工作流：
    1. MinerU文档提取 → 2. 云端LLM任务分解 → 3. omni-coder执行任务
    4. 任务过长保存 → 5. DeepAgent TodoList → 6. 云端LLM整合 → 7. 测试纠错
    8. omni-coder写注释 → 9. 代码格式化 → 10. 嵌入编码存储

    所有prompt从配置文件加载
    """

    # OMNI_CODER_PROMPT_COMMENT 是固定的，不从配置加载（它是给代码添加注释的系统行为）
    OMNI_CODER_PROMPT_COMMENT = """为以下代码添加注释和docstring：

```python
{code}
```

直接输出带注释的代码，不要解释。"""

    def __init__(self, model_manager: ModelManager, cloud_config: dict | None = None):
        self.model_manager = model_manager
        self.embedding_pipeline = EmbeddingPipeline(model_manager)

        # 云端LLM配置
        if cloud_config is None:
            with open("env.json", 'r',encoding="utf-8") as f:
                cloud_config = json.load(f)["MINIMAX"]

        self.cloud_llm = ChatAnthropic(
            model=cloud_config["model"],
            base_url=cloud_config["base_url"],
            api_key=cloud_config["key"],
            temperature=0.7
        )

        # 从配置加载cloud prompts
        self.minimax_prompt_decompose = cloud_config.get("prompt", "")
        # 以下为固定使用的cloud prompt（整合、测试）
        self.MINIMAX_PROMPT_INTEGRATE = """你是一个代码整合专家。将多个函数实现整合为完整的代码文件。
确保函数顺序正确，添加必要的导入语句。
直接输出整合后的代码，不需要解释。"""

        self.MINIMAX_PROMPT_TEST_FIX = """你是一个代码审查专家。检查代码中的错误并给出修复建议。
如果代码没有问题，输出"OK"。
如果有错误，输出修复后的代码。"""

        self.filesystem = FilesystemBackend(root_dir="./workspace", virtual_mode=True)

    def run(self, document_content: str) -> WorkflowResult:
        """执行完整工作流

        Args:
            document_content: 文档内容（来自MinerU提取）

        Returns:
            WorkflowResult: 工作流执行结果
        """
        tasks = self._step2_decompose(document_content)
        code_results = self._step3_execute_tasks(tasks)
        code = self._step6_integrate(code_results)
        code = self._step7_test_and_fix(code)
        code = self._step8_write_comments(code)
        # TODO: 嵌入功能暂禁用，需要LM Studio支持
        # self._step10_embed_and_store(code)

        return WorkflowResult(
            code=code,
            embedding_path="./workspace/embeddings.pkl",
            tasks=tasks,
            results=code_results
        )

    # MiniMax返回camelCase字段名的映射
    _FIELD_MAPPING = {
        # 英文camelCase
        "functionName": "function_name",
        "returnType": "output_type",
        # 中文键名
        "函数名": "function_name",
        "参数列表": "parameters",
        "返回值类型": "output_type",
        "功能描述": "description",
    }

    def _normalize_task_fields(self, t: dict) -> dict:
        """规范化MiniMax返回的字段名"""
        result = {}
        for key, value in t.items():
            norm_key = self._FIELD_MAPPING.get(key, key)
            result[norm_key] = value

        # 解析参数列表（可能是数组或字符串）
        if "parameters" in result:
            result["parameters"] = self._parse_parameters(result["parameters"])

        # 添加空dependencies
        if "dependencies" not in result:
            result["dependencies"] = []

        return result

    def _parse_parameters(self, param_value) -> list:
        """解析参数列表（支持数组和字符串格式）"""
        if isinstance(param_value, list):
            # MiniMax返回: [{"参数名": "a", "参数类型": "number", "描述": "..."}, ...]
            params = []
            for p in param_value:
                if isinstance(p, dict):
                    params.append({
                        "name": p.get("参数名", p.get("name", "")),
                        "type": p.get("参数类型", p.get("type", "Any")),
                        "description": p.get("描述", p.get("description", "")),
                        "required": True
                    })
            return params
        elif isinstance(param_value, str):
            # 字符串格式: "a: float, b: float"
            return self._parse_parameters_string(param_value)
        return []

    def _step2_decompose(self, doc_content: str) -> list[Task]:
        """步骤2: 云端LLM分解任务"""
        prompt = f"{self.minimax_prompt_decompose}\n\n文档内容：\n{doc_content}"
        response = self.cloud_llm.invoke(prompt)
        content = self._extract_content(response)

        # 尝试解析JSON（可能包含markdown代码块）
        json_str = self._extract_json_from_markdown(content)

        try:
            tasks_data = json.loads(json_str)
            tasks = []
            for t in tasks_data:
                # 规范化字段名
                t = self._normalize_task_fields(t)
                tasks.append(Task(**t))
        except Exception as e:
            tasks = [Task(
                function_name="default_func",
                parameters=[],
                output_type="Any",
                description=content[:500],
                dependencies=[]
            )]

        return tasks

    def _step3_execute_tasks(self, tasks: list[Task]) -> list[CodeResult]:
        """步骤3: omni-coder逐个完成任务"""
        coder_prompt_template = self.model_manager.get_coder_prompt()
        self.model_manager.load_coder()
        coder = self.model_manager.get_coder()

        results = []
        for task in tasks:
            # 使用配置中的prompt模板
            prompt = coder_prompt_template.format(
                description=task["description"],
                function_name=task["function_name"],
                parameters=json.dumps(task["parameters"]),
                output_type=task["return_type"]
            )

            try:
                result = coder.respond(prompt)
                code = result.content if hasattr(result, 'content') else str(result)
                results.append(CodeResult(
                    task=task,
                    code=code,
                    status="success",
                    error=None
                ))
            except Exception as e:
                results.append(CodeResult(
                    task=task,
                    code="",
                    status="error",
                    error=str(e)
                ))

        return results

    def _step4_handle_long_todo(self, tasks: list[Task]) -> list[Task]:
        """步骤4: 任务过长则保存到FilesystemBackend (Pickle格式)"""
        if len(json.dumps(tasks)) > 5000:
            self.filesystem.write("long_tasks.pkl", pickle.dumps(tasks))
            return []
        return tasks

    def _step6_integrate(self, code_results: list[CodeResult]) -> str:
        """步骤6: 云端LLM整合代码"""
        code_snippets = "\n\n".join([r["code"] for r in code_results if r["status"] == "success"])
        prompt = f"{self.MINIMAX_PROMPT_INTEGRATE}\n\n代码片段：\n{code_snippets}"

        response = self.cloud_llm.invoke(prompt)
        content = self._extract_content(response)

        # 从markdown代码块中提取纯代码
        return self._extract_json_from_markdown(content)

    def _extract_content(self, response) -> str:
        """从响应中提取字符串内容

        MiniMax返回的content是包含signature/thinking/text字段的字典列表。
        优先使用response.text获取纯文本部分。
        """
        # 优先使用response.text（langchain_core会自动提取text字段）
        if hasattr(response, 'text'):
            return response.text

        # 否则手动从content列表中提取text字段
        if hasattr(response, 'content'):
            content = response.content
            if isinstance(content, list):
                parts = []
                for block in content:
                    if isinstance(block, dict):
                        # MiniMax格式: {'type': 'text', 'text': '...'}
                        if block.get('type') == 'text' and 'text' in block:
                            parts.append(block['text'])
                        # 跳过thinking类型
                        elif block.get('type') == 'thinking':
                            continue
                        else:
                            parts.append(str(block))
                    elif hasattr(block, 'text'):
                        parts.append(block.text)
                    else:
                        parts.append(str(block))
                return "".join(parts)
            return str(content)
        return str(response)

    def _extract_json_from_markdown(self, text: str) -> str:
        """从markdown代码块中提取内容（JSON或普通代码）"""
        import re
        # 匹配 ```lang ... ``` 或 ``` ... ```，捕获语言标识符后的内容
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',   # ```json ... ```
            r'```python\s*([\s\S]*?)\s*```',  # ```python ... ```
            r'```\w*\s*([\s\S]*?)\s*```',    # ```任意语言 ... ```
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return text

    def _step7_test_and_fix(self, code: str) -> str:
        """步骤7: 测试纠错循环（最多3次）

        MiniMax可能返回:
        - "OK" 或 "✅ OK" 表示代码无问题
        - ```python code ``` 表示修复后的代码
        - Markdown格式的报告，需要解析
        """
        for _ in range(3):
            prompt = f"{self.MINIMAX_PROMPT_TEST_FIX}\n\n代码：\n{code}"
            response = self.cloud_llm.invoke(prompt)
            result = self._extract_content(response)

            # 检查是否表示OK（可能是 "OK", "✅ OK", "**状态**: OK 等）
            stripped = result.strip()
            if stripped == "OK" or "✅ OK" in result or "状态" in result and "OK" in result:
                # 进一步检查是否真的只是OK，没有错误修复
                if "```python" not in result:
                    return code

            # 提取markdown代码块中的代码
            import re
            code_match = re.search(r'```python\s*([\s\S]*?)\s*```', result)
            if code_match:
                fixed_code = code_match.group(1).strip()
                if fixed_code:
                    code = fixed_code
                    continue

            # 如果有实质性修复建议但没有代码块，用原始代码继续
            if "错误" in result or "修复" in result or "问题" in result:
                continue

            # 没有明确的修复意见，保持原代码
            break

        return code

    def _step8_write_comments(self, code: str) -> str:
        """步骤8: omni-coder写注释（按函数拆分处理）"""
        self.model_manager.load_coder()
        coder = self.model_manager.get_coder()

        # 按函数拆分代码
        functions = self._split_code_into_functions(code)
        commented_functions = []

        for func in functions:
            if func.strip():
                prompt = self.OMNI_CODER_PROMPT_COMMENT.format(code=func)
                result = coder.respond(prompt)
                # LM Studio返回PredictionResult，需要提取content
                content = result.content if hasattr(result, 'content') else str(result)
                # 提取markdown代码块中的纯代码（处理thinking和markdown包裹）
                content = self._extract_json_from_markdown(content)
                commented_functions.append(content)

        return "\n\n".join(commented_functions)

    def _split_code_into_functions(self, code: str) -> list[str]:
        """将代码按函数拆分为列表"""
        import re
        pattern = r'^(?:def |class |async def )'
        lines = code.split('\n')
        functions = []
        current = []

        for line in lines:
            if re.match(pattern, line) and current:
                functions.append('\n'.join(current))
                current = []
            current.append(line)

        if current:
            functions.append('\n'.join(current))

        return functions if functions else [code]

    def _step10_embed_and_store(self, code: str):
        """步骤10: 嵌入编码并存储"""
        self.embedding_pipeline.embed_and_store(code)