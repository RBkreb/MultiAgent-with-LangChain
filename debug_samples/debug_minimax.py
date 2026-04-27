import sys
sys.path.insert(0, 'E:/LangAgent')
import json
import re

from langchain_anthropic import ChatAnthropic

with open('env.json', 'r', encoding='utf-8') as f:
    cloud_config = json.load(f)['MINIMAX']

llm = ChatAnthropic(
    model=cloud_config['model'],
    base_url=cloud_config['base_url'],
    api_key=cloud_config['key'],
    temperature=0.7
)

prompt = cloud_config['prompt'] + '''

文档内容：
1. 实现一个计算器类，包含加、减、乘、除运算
2. 返回结果需要保留2位小数'''

response = llm.invoke(prompt)
result = response.text

# Save raw response
with open('E:/LangAgent/debug_raw_response.txt', 'w', encoding='utf-8') as f:
    f.write(result)

# Extract JSON
match = re.search(r'```json\s*([\s\S]*?)\s*```', result)
if match:
    json_str = match.group(1)
    tasks = json.loads(json_str)
    print(f'Parsed {len(tasks)} tasks')
    print('First task keys:', list(tasks[0].keys()))
else:
    print('No JSON found')
    print('Result[:500]:', result[:500])