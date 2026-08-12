# -*- coding: utf-8 -*-
"""无极提示词翻译节点。"""

try:
    from ..utils import config, llm_api
except ImportError:  # 直接执行时的回退方案
    from utils import config, llm_api


class WujiPromptTranslator:
    CATEGORY = "无极 Wuji/反推"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("翻译结果",)
    FUNCTION = "translate"

    @classmethod
    def INPUT_TYPES(cls):
        saved = config.load_config(force=True)
        return {
            "required": {
                "提示词": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "API密钥": (
                    "STRING",
                    {
                        "default": saved.get("api_key", ""),
                        "multiline": False,
                        "placeholder": "填入 sk-... 后执行一次即会自动保存",
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
                "保存密钥设置": ("BOOLEAN", {"default": True}),
                "目标语言": (["英文", "中文", "日文", "韩文", "法文", "俄文", "西班牙文"],),
                "源语言": (["自动检测", "中文", "英文", "日文", "韩文", "法文", "俄文", "西班牙文"],),
                "保留标签格式": ("BOOLEAN", {"default": False}),
                "额外要求": (
                    "STRING",
                    {"multiline": True, "default": "", "placeholder": "选填：补充说明"},
                ),
            },
        }

    def translate(
        self,
        提示词="",
        API密钥="",
        API网址="",
        模型名称="",
        保存密钥设置=True,
        目标语言="英文",
        源语言="自动检测",
        保留标签格式=False,
        额外要求="",
    ):
        if 保存密钥设置 and (API密钥.strip() or API网址.strip() or 模型名称.strip()):
            config.save_config(
                api_key=API密钥,
                base_url=API网址,
                model=模型名称,
            )

        result = llm_api.translate_prompt(
            text=提示词,
            target_lang=目标语言,
            source_lang=源语言,
            keep_tags=保留标签格式,
            extra_hint=额外要求,
            api_key=API密钥,
            base_url=API网址,
            model=模型名称,
        )
        return (result,)
