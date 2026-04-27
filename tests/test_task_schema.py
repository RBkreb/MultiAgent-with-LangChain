import sys
sys.path.insert(0, 'E:/LangAgent')

import pytest
from core.task_schema import Task, Parameter, CodeResult, WorkflowResult


class TestTaskSchema:
    """TaskSchema单元测试"""

    def test_parameter_creation(self):
        """测试Parameter创建"""
        param = Parameter(
            name="x",
            type="int",
            description="输入数字",
            required=True
        )
        assert param["name"] == "x"
        assert param["type"] == "int"
        assert param["required"] is True

    def test_task_creation(self):
        """测试Task创建"""
        task = Task(
            function_name="add",
            parameters=[Parameter(name="x", type="int", description="", required=True)],
            output_type="int",
            description="两数相加",
            dependencies=[]
        )
        assert task["function_name"] == "add"
        assert task["output_type"] == "int"
        assert len(task["parameters"]) == 1

    def test_task_with_dependencies(self):
        """测试带依赖的任务"""
        task = Task(
            function_name="main",
            parameters=[],
            output_type="None",
            description="主函数",
            dependencies=["init", "process"]
        )
        assert len(task["dependencies"]) == 2
        assert "init" in task["dependencies"]

    def test_code_result_creation(self):
        """测试CodeResult创建"""
        task = Task(
            function_name="test",
            parameters=[],
            output_type="str",
            description="测试",
            dependencies=[]
        )
        result = CodeResult(
            task=task,
            code="def test(): pass",
            status="success",
            error=None
        )
        assert result["status"] == "success"
        assert result["task"]["function_name"] == "test"

    def test_workflow_result_creation(self):
        """测试WorkflowResult创建"""
        task = Task(
            function_name="test",
            parameters=[],
            output_type="str",
            description="测试",
            dependencies=[]
        )
        result = CodeResult(
            task=task,
            code="def test(): pass",
            status="success",
            error=None
        )
        workflow = WorkflowResult(
            code="def test(): pass",
            embedding_path="./embeddings.pkl",
            tasks=[task],
            results=[result]
        )
        assert workflow["code"] == "def test(): pass"
        assert len(workflow["tasks"]) == 1

    def test_task_serialization(self):
        """测试Task序列化/反序列化"""
        task = Task(
            function_name="serialize_test",
            parameters=[
                Parameter(name="data", type="str", description="数据", required=True)
            ],
            output_type="bool",
            description="测试序列化",
            dependencies=[]
        )
        import json
        serialized = json.dumps(task, ensure_ascii=False)
        deserialized = json.loads(serialized)

        assert deserialized["function_name"] == "serialize_test"
        assert deserialized["parameters"][0]["name"] == "data"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])