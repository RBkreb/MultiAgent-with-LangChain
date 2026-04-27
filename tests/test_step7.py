import sys
sys.path.insert(0, 'E:/LangAgent')
import json
from unittest.mock import Mock

# Mock LM Studio
class MockCoder:
    def respond(self, prompt):
        result = Mock()
        result.content = f'# Code for: {prompt[:50]}\ndef test():\n    pass'
        return result
    def unload(self):
        pass

sys.modules['lmstudio'] = type('MockLMS', (), {
    'llm': lambda self, n, c=None: MockCoder(),
    'embedding_model': lambda self, n: MockCoder()
})()

from core.workflow_orchestrator import WorkflowOrchestrator
from core.model_manager import ModelManager

with open('env.json', 'r', encoding='utf-8') as f:
    env_config = json.load(f)

model_manager = ModelManager(env_config.get('LOCAL', {}))
orchestrator = WorkflowOrchestrator(model_manager, env_config.get('MINIMAX', {}))

# Load step7 response
with open('debug_step7_response.json', 'r', encoding='utf-8') as f:
    saved7 = json.load(f)

class MockCloudLLM:
    def invoke(self, prompt):
        response = Mock()
        if '审查' in prompt or '测试' in prompt or '纠错' in prompt:
            response.text = saved7['text']
            response.content = saved7['content']
        else:
            response.text = 'OK'
        return response

orchestrator.cloud_llm = MockCloudLLM()

# Test step7
test_code = 'def add(a, b):\n    return round(a + b, 2)'
print('Input code:')
print(test_code)
print()
result = orchestrator._step7_test_and_fix(test_code)
print('Step7 output:')
print(result)
print()
print('Is same as input:', result == test_code)