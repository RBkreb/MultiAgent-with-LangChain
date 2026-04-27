import sys
sys.path.insert(0, 'E:/LangAgent')

import pytest
from unittest.mock import Mock, patch, MagicMock
from core.workflow_orchestrator import WorkflowOrchestrator
from core.model_manager import ModelManager
from core.task_schema import Task, CodeResult


CLOUD_CONFIG = {
    "model": "minimax/MiniMax-M2.7",
    "key": "test-key",
    "base_url": "https://api.minimaxi.com/anthropic"
}


class TestWorkflowOrchestrator:
    """WorkflowOrchestrator单元测试"""

    def setup_method(self):
        """每个测试前创建模拟组件"""
        self.mock_mm = Mock(spec=ModelManager)
        self.mock_coder = Mock()
        self.mock_embedding = Mock()
        self.mock_mm.get_coder.return_value = self.mock_coder
        self.mock_mm.get_embedding.return_value = self.mock_embedding
        self.mock_mm.load_coder = Mock()

    def test_initialization(self):
        """测试初始化"""
        orch = WorkflowOrchestrator(self.mock_mm, CLOUD_CONFIG)
        assert orch.model_manager == self.mock_mm
        assert orch.embedding_pipeline is not None

    def test_step2_decompose_with_mock(self):
        """测试任务分解（模拟）"""
        orch = WorkflowOrchestrator(self.mock_mm, CLOUD_CONFIG)

        mock_response = Mock()
        mock_response.content = '[{"function_name":"test","parameters":[],"output_type":"str","description":"测试","dependencies":[]}]'
        mock_response.text = '[{"function_name":"test","parameters":[],"output_type":"str","description":"测试","dependencies":[]}]'

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        orch.cloud_llm = mock_llm

        tasks = orch._step2_decompose("测试文档")
        assert len(tasks) == 1
        assert tasks[0]["function_name"] == "test"

    def test_step3_execute_tasks_with_mock(self):
        """测试任务执行（模拟）"""
        orch = WorkflowOrchestrator(self.mock_mm, CLOUD_CONFIG)

        task = Task(
            function_name="add",
            parameters=[],
            output_type="int",
            description="两数相加",
            dependencies=[]
        )

        self.mock_coder.respond.return_value = "def add(a, b):\n    return a + b"

        results = orch._step3_execute_tasks([task])
        assert len(results) == 1
        assert results[0]["status"] == "success"
        assert "def add" in results[0]["code"]

    def test_step4_handle_long_todo(self):
        """测试长任务保存"""
        orch = WorkflowOrchestrator(self.mock_mm, CLOUD_CONFIG)

        long_task = Task(
            function_name="large_func",
            parameters=[{"name": f"p{i}", "type": "int", "description": "", "required": True} for i in range(50)],
            output_type="str",
            description="x" * 6000,
            dependencies=[]
        )

        result = orch._step4_handle_long_todo([long_task])
        assert result == []

    def test_step6_integrate(self):
        """测试代码整合"""
        orch = WorkflowOrchestrator(self.mock_mm, CLOUD_CONFIG)

        mock_response = Mock()
        mock_response.content = "def main(): pass\nclass Test: pass"
        mock_response.text = "def main(): pass\nclass Test: pass"

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        orch.cloud_llm = mock_llm

        results = [
            CodeResult(task=Task(function_name="main", parameters=[], output_type="None", description="", dependencies=[]), code="def main(): pass", status="success", error=None),
            CodeResult(task=Task(function_name="Test", parameters=[], output_type="type", description="", dependencies=[]), code="class Test: pass", status="success", error=None)
        ]

        code = orch._step6_integrate(results)
        assert "def main" in code
        assert "class Test" in code

    def test_step7_test_and_fix(self):
        """测试测试纠错"""
        orch = WorkflowOrchestrator(self.mock_mm, CLOUD_CONFIG)

        mock_response = Mock()
        mock_response.content = "OK"
        mock_response.text = "OK"

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        orch.cloud_llm = mock_llm

        code = orch._step7_test_and_fix("def test(): pass")
        assert "def test" in code

    def test_step8_write_comments(self):
        """测试写注释"""
        orch = WorkflowOrchestrator(self.mock_mm, CLOUD_CONFIG)

        self.mock_coder.respond.return_value = 'def add(a, b):\n    """Add two numbers"""'

        code = orch._step8_write_comments("def add(a, b):\n    return a + b")
        assert "add" in code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])