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

# Step 2: 任务分解
prompt_decompose = cloud_config['prompt'] + '''

文档内容：
1. 实现一个计算器类，包含加、减、乘、除运算
2. 返回结果需要保留2位小数'''

response = llm.invoke(prompt_decompose)
result = response.text

with open('E:/LangAgent/debug_step2_response.json', 'w', encoding='utf-8') as f:
    json.dump({
        'text': result,
        'content': response.content
    }, f, ensure_ascii=False, indent=2)

print('Step 2 response saved to debug_step2_response.json')
print('Length:', len(result))

# Step 6: 代码整合
prompt_integrate = '''你是一个代码整合专家。将多个函数实现整合为完整的代码文件。
确保函数顺序正确，添加必要的导入语句。
直接输出整合后的代码，不需要解释。

代码片段：
def add(num1, num2):
    return round(num1 + num2, 2)

def subtract(num1, num2):
    return round(num1 - num2, 2)'''

response6 = llm.invoke(prompt_integrate)
with open('E:/LangAgent/debug_step6_response.json', 'w', encoding='utf-8') as f:
    json.dump({
        'text': response6.text,
        'content': response6.content
    }, f, ensure_ascii=False, indent=2)
print('Step 6 response saved')

# Step 7: 测试纠错
prompt_test = '''你是一个代码审查专家。检查代码中的错误并给出修复建议。
如果代码没有问题，输出"OK"。
如果有错误，输出修复后的代码。

代码：
def add(num1, num2):
    return round(num1 + num2, 2)

def subtract(num1, num2):
    return round(num1 - num2, 2)'''

response7 = llm.invoke(prompt_test)
with open('E:/LangAgent/debug_step7_response.json', 'w', encoding='utf-8') as f:
    json.dump({
        'text': response7.text,
        'content': response7.content
    }, f, ensure_ascii=False, indent=2)
print('Step 7 response saved')