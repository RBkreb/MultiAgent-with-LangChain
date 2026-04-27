import sys
sys.path.insert(0, 'E:/LangAgent')
import json
import re
from unittest.mock import Mock

# Mock LM Studio
class MockCoder:
    def respond(self, prompt):
        result = Mock()
        result.content = f'# Commented: {prompt[:50]}\ndef test():\n    pass'
        return result
    def unload(self):
        pass

sys.modules['lmstudio'] = type('MockLMS', (), {
    'llm': lambda self, n, c=None: MockCoder(),
    'embedding_model': lambda self, n: MockCoder()
})()

# Load step7 response
with open('debug_step7_response.json', 'r', encoding='utf-8') as f:
    saved7 = json.load(f)

result = saved7['text']
print('=== Step7 Response ===')
print(result)
print()

# Test extraction
stripped = result.strip()
print('=== Checks ===')
print(f'stripped == "OK": {stripped == "OK"}')
print(f'"✅ OK" in result: {"✅ OK" in result}')
print(f'"```python" in result: {"```python" in result}')
print()

# Extract code
code_match = re.search(r'```python\s*([\s\S]*?)\s*```', result)
if code_match:
    fixed_code = code_match.group(1).strip()
    print('=== Extracted Code ===')
    print(fixed_code)