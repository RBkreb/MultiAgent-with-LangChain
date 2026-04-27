import sys
sys.path.insert(0, 'E:/LangAgent')
import json

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

# Extract JSON from markdown
import re
match = re.search(r'```json\s*([\s\S]*?)\s*```', result)
if match:
    json_str = match.group(1)
    tasks = json.loads(json_str)
    print('Tasks count:', len(tasks))
    for i, t in enumerate(tasks):
        print(f'\nTask {i} keys: {list(t.keys())}')
        print(f'Task {i}: {json.dumps(t, ensure_ascii=False)}')
else:
    print('No JSON code block found')
    print('Response text:')
    print(result[:1000])