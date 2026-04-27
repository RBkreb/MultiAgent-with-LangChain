import sys
sys.path.insert(0, 'E:/LangAgent')

import pytest
from core.model_manager import ModelManager


class TestModelManager:
    """ModelManager单元测试"""

    def setup_method(self):
        """每个测试方法前创建新的ModelManager实例"""
        self.mm = ModelManager()

    def teardown_method(self):
        """每个测试方法后清理"""
        if self.mm is not None:
            self.mm.unload()

    def test_initial_state(self):
        """测试初始状态"""
        assert self.mm.current_type is None
        assert self.mm._current_model is None
        assert not self.mm.is_coder_loaded()
        assert not self.mm.is_embedding_loaded()

    def test_load_coder_sets_type(self):
        """测试加载coder后类型正确"""
        self.mm.load_coder("omni-coder-9b")
        assert self.mm.current_type == "coder"
        assert self.mm.is_coder_loaded()
        assert not self.mm.is_embedding_loaded()

    def test_load_embedding_sets_type(self):
        """测试加载embedding后类型正确"""
        self.mm.load_embedding("qwen3-embedding-0.6B")
        assert self.mm.current_type == "embedding"
        assert self.mm.is_embedding_loaded()
        assert not self.mm.is_coder_loaded()

    def test_exclusive_loading(self):
        """测试互斥加载：加载embedding时coder应被卸载"""
        self.mm.load_coder("omni-coder-9b")
        assert self.mm.is_coder_loaded()

        self.mm.load_embedding("qwen3-embedding-0.6B")
        assert self.mm.is_embedding_loaded()
        assert not self.mm.is_coder_loaded()

    def test_context_limit_configured(self):
        """测试omni-coder的上下文长度配置"""
        assert ModelManager.OMNI_CODER_CONTEXT_LIMIT == 8192

    def test_unload_clears_state(self):
        """测试卸载后状态正确"""
        self.mm.load_coder("omni-coder-9b")
        self.mm.unload()

        assert self.mm.current_type is None
        assert not self.mm.is_coder_loaded()
        assert not self.mm.is_embedding_loaded()

    def test_get_coder_auto_loads(self):
        """测试get_coder自动加载"""
        model = self.mm.get_coder()
        assert model is not None
        assert self.mm.is_coder_loaded()

    def test_get_embedding_auto_loads(self):
        """测试get_embedding自动加载"""
        model = self.mm.get_embedding()
        assert model is not None
        assert self.mm.is_embedding_loaded()

    def test_idempotent_coder_load(self):
        """测试重复加载coder是幂等的"""
        self.mm.load_coder("omni-coder-9b")
        first_model = self.mm._current_model

        self.mm.load_coder("omni-coder-9b")
        second_model = self.mm._current_model

        assert first_model is second_model

    def test_idempotent_embedding_load(self):
        """测试重复加载embedding是幂等的"""
        self.mm.load_embedding("qwen3-embedding-0.6B")
        first_model = self.mm._current_model

        self.mm.load_embedding("qwen3-embedding-0.6B")
        second_model = self.mm._current_model

        assert first_model is second_model


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
