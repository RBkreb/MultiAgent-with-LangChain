from typing import TypedDict


class Parameter(TypedDict):
    """函数参数定义"""
    name: str
    type: str
    description: str
    required: bool


class Task(TypedDict):
    """分解后的任务单元

    用于标准化函数实现的描述格式
    """
    function_name: str
    parameters: list[Parameter]
    output_type: str
    description: str
    dependencies: list[str]  # 依赖的其他任务名


class CodeResult(TypedDict):
    """代码执行结果"""
    task: Task
    code: str
    status: str  # "success" | "error"
    error: str | None


class WorkflowResult(TypedDict):
    """完整工作流结果"""
    code: str
    embedding_path: str
    tasks: list[Task]
    results: list[CodeResult]