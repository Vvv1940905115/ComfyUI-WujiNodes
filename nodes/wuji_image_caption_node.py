# -*- coding: utf-8 -*-
"""无极图像反推提示词节点。"""

try:
    from ..utils import config, llm_api
except ImportError:  # 直接执行时的回退方案
    from utils import config, llm_api


class WujiImageCaption:
    CATEGORY = "工坊提示词/反推"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("反推提示词",)
    FUNCTION = "reverse"

    @classmethod
    def INPUT_TYPES(cls):
        saved = config.load_config(force=True)
        return {
            "required": {
                "图像": ("IMAGE",),
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
                "扩写模式": (
                    [
                        "通用",
                        "人像大师",
                        "Tags 风格",
                        "电影镜头视觉",
                        "光影质感视觉",
                        "氛围场景视觉",
                        "美学构图视觉",
                    ],
                ),
                "提示词风格": (["详细描述", "简短标签", "英文提示词", "中英混合"],),
                "额外要求": (
                    "STRING",
                    {"multiline": True, "default": "", "placeholder": "选填：补充说明"},
                ),
            },
        }

    def reverse(
        self,
        图像,
        API密钥="",
        API网址="",
        模型名称="",
        保存密钥设置=True,
        扩写模式="通用",
        提示词风格="详细描述",
        额外要求="",
    ):
        if 保存密钥设置 and (API密钥.strip() or API网址.strip() or 模型名称.strip()):
            config.save_config(
                api_key=API密钥,
                base_url=API网址,
                model=模型名称,
            )

        prompt = llm_api.reverse_prompt(
            image_np=图像,
            is_video=False,
            mode=扩写模式,
            style=提示词风格,
            extra_hint=额外要求,
            api_key=API密钥,
            base_url=API网址,
            model=模型名称,
        )
        return (prompt,)
