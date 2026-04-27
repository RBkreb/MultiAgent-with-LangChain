import sys
sys.path.insert(0, 'E:/LangAgent')

import pytest
import pickle
import os
import tempfile
from core.embedding_pipeline import EmbeddingPipeline
from core.model_manager import ModelManager


class TestEmbeddingPipeline:
    """EmbeddingPipeline单元测试"""

    def setup_method(self):
        """每个测试前创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.mm = ModelManager()
        self.pipeline = EmbeddingPipeline(self.mm, self.temp_dir)

    def teardown_method(self):
        """清理临时目录"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_extract_functions(self):
        """测试函数提取"""
        code = '''
def add(a, b):
    """Add two numbers"""
    return a + b

def multiply(x, y):
    return x * y
'''
        items = self.pipeline._extract_functions_and_comments(code)
        assert any("def add" in item for item in items)
        assert any("def multiply" in item for item in items)

    def test_extract_comments(self):
        """测试注释提取"""
        code = '''
# This is a comment
def test():
    pass
'''
        items = self.pipeline._extract_functions_and_comments(code)
        assert any("# This is a comment" in item for item in items)

    def test_embed_and_store(self):
        """测试嵌入存储（需要LM Studio运行）"""
        code = '''
def hello():
    """Say hello"""
    print("Hello")
'''
        path = self.pipeline.embed_and_store(code)
        assert path == "embeddings.pkl"

        # 验证通过backend读取
        result = self.pipeline.backend.read("embeddings.pkl")
        assert result.error is None
        content = result.file_data.get("content", "")
        assert content is not None
        import base64
        import pickle
        embeddings = pickle.loads(base64.b64decode(content))
        assert len(embeddings) > 0
        assert "item" in embeddings[0]
        assert "embedding" in embeddings[0]

    def test_load_embeddings(self):
        """测试加载嵌入"""
        code = '''
def test_func():
    pass
'''
        self.pipeline.embed_and_store(code)
        loaded = self.pipeline.load_embeddings()
        assert len(loaded) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])