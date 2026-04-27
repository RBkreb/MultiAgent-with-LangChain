import sys
sys.path.insert(0, 'E:/LangAgent')
import json
from unittest.mock import Mock

# Mock LM Studio
class MockCoder:
    def respond(self, prompt):
        result = Mock()
        result.content = f'def {prompt.split()[2]}(a, b):\n    return round(a + b, 2)'
        return result
    def unload(self):
        pass

sys.modules['lmstudio'] = type('MockLMS', (), {
    'llm': lambda self, n, c=None: MockCoder(),
    'embedding_model': lambda self, n: MockCoder()
})()

from core.workflow_orchestrator import WorkflowOrchestrator
from core.model_manager import ModelManager
from core.task_schema import Task, CodeResult

with open('env.json', 'r', encoding='utf-8') as f:
    env_config = json.load(f)

model_manager = ModelManager(env_config.get('LOCAL', {}))
orchestrator = WorkflowOrchestrator(model_manager, env_config.get('MINIMAX', {}))

# Mock step6 to use saved response
with open('debug_step6_response.json', 'r', encoding='utf-8') as f:
    saved6 = json.load(f)

class MockCloudLLM:
    def invoke(self, prompt):
        response = Mock()
        if '整合' in prompt:
            response.text = saved6['text']
            response.content = saved6['content']
        elif '审查' in prompt or '测试' in prompt or '纠错' in prompt:
            with open('debug_step7_response.json', 'r', encoding='utf-8') as f:
                saved7 = json.load(f)
            response.text = saved7['text']
            response.content = saved7['content']
        else:
            response.text = 'OK'
        return response

orchestrator.cloud_llm = MockCloudLLM()

# Simulate step3 results
code_results = [
    CodeResult(
        task=Task(function_name='add', parameters=[], output_type='float', description='加法', dependencies=[]),
        code='def add(a, b):\n    return round(a + b, 2)',
        status='success',
        error=None
    ),
    CodeResult(
        task=Task(function_name='subtract', parameters=[], output_type='float', description='减法', dependencies=[]),
        code='def subtract(a, b):\n    return round(a - b, 2)',
        status='success',
        error=None
    ),
]

print('=== Step 6: 整合 ===')
integrated = orchestrator._step6_integrate(code_results)
print('整合结果:')
print(integrated[:500] if len(integrated) > 500 else integrated)

print('\n=== Step 7: 测试纠错 ===')
test_result = orchestrator._step7_test_and_fix(integrated)
print('测试纠错结果:')
print(test_result[:500] if len(test_result) > 500 else test_result)