import pickle
import base64
from typing import Any
from core.model_manager import ModelManager
from deepagents.backends import FilesystemBackend


class EmbeddingPipeline:
    """代码嵌入编码管道

    将代码片段（函数名、注释）转换为向量并存储到FilesystemBackend
    """

    def __init__(self, model_manager: ModelManager, output_dir: str = "./embeddings"):
        self.model_manager = model_manager
        self.backend = FilesystemBackend(root_dir=output_dir, virtual_mode=True)

    def embed_and_store(self, code: str) -> str:
        """嵌入编码并存储到FilesystemBackend

        Args:
            code: 代码字符串

        Returns:
            保存的文件路径
        """
        self.model_manager.load_embedding()
        embedding_model = self.model_manager.get_embedding()

        items = self._extract_functions_and_comments(code)
        embeddings = []

        for item in items:
            emb = embedding_model.embed(item)
            embeddings.append({"item": item, "embedding": emb})

        output_path = "embeddings.pkl"
        # FilesystemBackend.write expects str, so encode bytes to base64
        data = base64.b64encode(pickle.dumps(embeddings)).decode('utf-8')
        self.backend.write(output_path, data)
        return output_path

    def _extract_functions_and_comments(self, code: str) -> list[str]:
        """从代码中提取函数名和注释"""
        import re

        items = []
        lines = code.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("def "):
                items.append(stripped)
            elif stripped.startswith("#"):
                items.append(stripped)
            elif stripped.startswith('"""') or stripped.startswith("'''"):
                if len(stripped) > 6:
                    items.append(stripped)

        return items

    def load_embeddings(self) -> list[dict[str, Any]]:
        """从FilesystemBackend加载嵌入数据"""
        try:
            result = self.backend.read("embeddings.pkl")
            if result.error:
                return []
            content = result.file_data.get("content", "")
            return pickle.loads(base64.b64decode(content))
        except Exception:
            return []