"""MultiAgents Coder 主入口

多智能体编码系统，整合云端LLM（MiniMax）和本地LLM（LM Studio）
"""
import sys
sys.path.insert(0, 'E:/LangAgent')
import json

from core.workflow_orchestrator import WorkflowOrchestrator
from core.model_manager import ModelManager


def main():
    """主入口"""
    # 加载配置
    with open('env.json', 'r', encoding='utf-8') as f:
        env_config = json.load(f)

    model_manager = ModelManager(env_config.get('LOCAL', {}))
    orchestrator = WorkflowOrchestrator(model_manager, env_config.get('MINIMAX', {}))

    # 示例文档内容
    document_content = """
    需求文档：
    1. 实现一个计算器类，包含加、减、乘、除运算
    2. 返回结果需要保留2位小数
    """

    print("开始执行工作流...")
    result = orchestrator.run(document_content)

    print(f"\n完成！")
    print(f"生成代码长度: {len(result['code'])} 字符")
    print(f"任务数量: {len(result['tasks'])}")
    print(f"\n=== 生成代码 ===\n{result['code']}")


if __name__ == "__main__":
    main()