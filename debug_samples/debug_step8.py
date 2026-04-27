import sys
sys.path.insert(0, 'E:/LangAgent')
import json
from unittest.mock import Mock

# Mock LM Studio
class MockCoder:
    def respond(self, prompt):
        result = Mock()
        print(f'  [MockCoder.respond] prompt[:80]: {repr(prompt[:80])}')
        result.content = f'# Commented\ndef add(a, b):\n    return round(a + b, 2)'
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

# Load step6 and step7 responses
with open('debug_step6_response.json', 'r', encoding='utf-8') as f:
    saved6 = json.load(f)
with open('debug_step7_response.json', 'r', encoding='utf-8') as f:
    saved7 = json.load(f)

class MockCloudLLM:
    def invoke(self, prompt):
        response = Mock()
        if '整合' in prompt:
            response.text = saved6['text']
            response.content = saved6['content']
        elif '审查' in prompt or '测试' in prompt or '纠错' in prompt:
            response.text = saved7['text']
            response.content = saved7['content']
        else:
            response.text = 'OK'
        return response

orchestrator.cloud_llm = MockCloudLLM()

# Test _extract_json_from_markdown
text = saved6['text']
print('=== Input to _extract_json_from_markdown ===')
print(repr(text[:100]))
print()

extracted = orchestrator._extract_json_from_markdown(text)
print('=== Extracted code ===')
print(repr(extracted[:100]))
print()

# Test split
functions = orchestrator._split_code_into_functions(extracted)
print(f'=== Split into {len(functions)} functions ===')
for i, f in enumerate(functions):
    print(f'Function {i}: {repr(f[:50])}')
print()

# Test step8
print('=== Step 8 processing ===')
result = orchestrator._step8_write_comments(extracted)
print(f'Final result ({len(result)} chars):')
print(result)