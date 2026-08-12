# -*- coding: utf-8 -*-
"""无极 API 设置节点：一次填写密钥并存入本地配置文件。"""

try:
    from ..utils import config
except ImportError:  # 直接执行时的回退方案
    from utils import config


class WujiApiSettings:
    CATEGORY = "无极 Wuji/设置"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("设置状态",)
    FUNCTION = "apply"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        saved = config.load_config(force=True)
        return {
            "required": {
                "API密钥": (
                    "STRING",
                    {
                        "default": saved.get("api_key", ""),
                        "multiline": False,
                        "placeholder": "填入 sk-... 后执行即保存到 config.json",
                    },
                ),
                "API网址": (
                    "STRING",
                    {"default": saved.get("base_url", config.DEFAULT_BASE_URL)},
                ),
                "模型名称": (
                    "STRING",
                    {"default": saved.get("model", config.DEFAULT_MODEL)},
                ),
            },
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")  # 永远重新执行，确保设置即时写入

    def apply(self, API密钥="", API网址="", 模型名称=""):
        ok = config.save_config(
            api_key=API密钥,
            base_url=API网址,
            model=模型名称,
        )
        cfg = config.load_config(force=True)
        status = "\n".join(
            [
                "保存成功" if ok else "保存失败",
                f"配置文件：{config.CONFIG_PATH}",
                f"API密钥：{config.mask(cfg.get('api_key', ''))}",
                f"API网址：{cfg.get('base_url', '')}",
                f"模型名称：{cfg.get('model', '')}",
            ]
        )
        print("[WujiNodes] " + status.replace("\n", " | "))
        return (status,)
