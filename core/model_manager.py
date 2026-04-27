import lmstudio as lms
from typing import Literal, Any


ModelType = Literal["coder", "embedding"]


class ModelConfig:
    """模型配置"""

    def __init__(self, model_name: str, base_url: str = "http://127.0.0.1:1234",
                 prompt: str = "", temperature: float = 0.7,
                 top_p: float = 0.9, top_k: int = 40):
        self.model_name = model_name
        self.base_url = base_url
        self.prompt = prompt
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k

    def to_lms_config(self) -> dict[str, Any]:
        """转换为LM Studio配置"""
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k
        }


class ModelManager:
    """LM Studio模型互斥管理器

    本地模型在显存受限环境下只能独占加载，此管理器确保：
    1. 同一时间只能加载一个模型
    2. 切换模型时自动卸载当前模型
    3. 提供统一的模型获取接口
    """

    OMNI_CODER_CONTEXT_LIMIT = 8192  # omni-coder-9B上下文长度限制

    def __init__(self, config: dict | None = None):
        self._current_model = None
        self._current_type: ModelType | None = None
        self._config = config or {}

    def load_coder(self, model_name: str | None = None, config: ModelConfig | None = None) -> None:
        """载入coder模型（与embedding模型互斥）"""
        if self._current_type == "coder" and self._current_model is not None:
            return

        self.unload()

        if config is None:
            coder_config = self._config.get("coder", {})
            if model_name is None:
                model_name = coder_config.get("model", "omni-coder-9b")
            config = ModelConfig(
                model_name=model_name,
                prompt=coder_config.get("prompt", ""),
                temperature=coder_config.get("temperature", 0.3),
                top_p=coder_config.get("top_p", 0.9),
                top_k=coder_config.get("top_k", 40)
            )

        self._current_model = lms.llm(config.model_name, config=config.to_lms_config())
        self._current_type = "coder"

    def load_embedding(self, model_name: str | None = None) -> None:
        """载入embedding模型（与coder模型互斥）"""
        if self._current_type == "embedding" and self._current_model is not None:
            return

        self.unload()

        if model_name is None:
            model_name = self._config.get("embedding", {}).get("model", "qwen3-embedding-0.6B")

        self._current_model = lms.embedding_model(model_name)
        self._current_type = "embedding"

    def unload(self) -> None:
        """卸载当前模型"""
        if self._current_model is not None:
            self._current_model.unload()
            self._current_model = None
            self._current_type = None

    def get_coder(self, model_name: str | None = None, config: ModelConfig | None = None):
        """获取当前coder模型实例（自动加载）"""
        if self._current_type != "coder" or self._current_model is None:
            self.load_coder(model_name, config)
        return self._current_model

    def get_embedding(self, model_name: str | None = None):
        """获取当前embedding模型实例（自动加载）"""
        if self._current_type != "embedding" or self._current_model is None:
            self.load_embedding(model_name)
        return self._current_model

    def get_coder_prompt(self) -> str:
        """获取coder的prompt模板"""
        return self._config.get("coder", {}).get("prompt", "")

    @property
    def current_type(self) -> ModelType | None:
        """返回当前加载的模型类型"""
        return self._current_type

    def is_coder_loaded(self) -> bool:
        """检查coder是否已加载"""
        return self._current_type == "coder" and self._current_model is not None

    def is_embedding_loaded(self) -> bool:
        """检查embedding模型是否已加载"""
        return self._current_type == "embedding" and self._current_model is not None

    def set_config(self, config: dict) -> None:
        """设置模型配置"""
        self._config = config

    def get_config(self) -> dict:
        """获取模型配置"""
        return self._config


if __name__ == "__main__":
    import json
    with open("env.json", 'r') as f:
        config = json.load(f)["LOCAL"]

    mm = ModelManager(config)
    mm.load_coder()
    print(f"Coder loaded: {mm.is_coder_loaded()}")
    print(f"Prompt: {mm.get_coder_prompt()[:50]}...")