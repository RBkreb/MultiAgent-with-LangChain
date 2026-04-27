"""测试工作流，使用保存的响应"""
import sys
sys.path.insert(0, 'E:/LangAgent')
import json
from unittest.mock import Mock, MagicMock

# 先mock lmstudio模块
class MockCoder:
    def respond(self, prompt):
        result = Mock()
        result.content = f"# Mocked code\ndef add(a, b):\n    return round(a + b, 2)"
        return result
    def unload(self):
        pass

class MockEmbedder:
    def embed(self, text):
        return [0.0] * 768
    def unload(self):
        pass

class MockLMStudio:
    def llm(self, name, config=None):
        return MockCoder()
    def embedding_model(self, name):
        return MockEmbedder()

# 替换lmstudio模块
sys.modules['lmstudio'] = MockLMStudio()

# 现在可以安全导入了
from core.workflow_orchestrator import WorkflowOrchestrator
from core.model_manager import ModelManager


def main():
    # 加载配置
    with open('env.json', 'r', encoding='utf-8') as f:
        env_config = json.load(f)

    model_manager = ModelManager(env_config.get('LOCAL', {}))
    orchestrator = WorkflowOrchestrator(model_manager, env_config.get('MINIMAX', {}))

    # Mock云端LLM使用保存的响应
    class MockCloudLLM:
        def invoke(self, prompt):
            response = Mock()
            if '任务分解' in prompt or '分解' in prompt:
                with open('debug_step2_response.json', 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                response.text = saved['text']
                response.content = saved['content']
            elif '整合' in prompt:
                with open('debug_step6_response.json', 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                response.text = saved['text']
                response.content = saved['content']
            elif '审查' in prompt or '测试' in prompt or '纠错' in prompt:
                with open('debug_step7_response.json', 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                response.text = saved['text']
                response.content = saved['content']
            else:
                response.text = "OK"
            return response

    orchestrator.cloud_llm = MockCloudLLM()

    document_content = """
    需求文档：
    1. 实现一个计算器类，包含加、减、乘、除运算
    2. 返回结果需要保留2位小数
    """

    print("开始执行工作流...")
    result = orchestrator.run(document_content)

    print(f"\n=== 结果 ===")
    print(f"生成代码长度: {len(result['code'])} 字符")
    print(f"任务数量: {len(result['tasks'])}")
    print(f"\n=== 代码内容 ===")
    print(result['code'])


if __name__ == "__main__":
    main()