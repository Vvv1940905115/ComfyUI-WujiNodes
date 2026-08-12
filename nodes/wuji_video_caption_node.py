# -*- coding: utf-8 -*-
"""无极视频反推提示词节点。"""

try:
    from ..utils import config, llm_api
except ImportError:  # 直接执行时的回退方案
    from utils import config, llm_api


class WujiVideoCaption:
    CATEGORY = "无极 Wuji/反推"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("反推提示词",)
    FUNCTION = "reverse"

    @classmethod
    def INPUT_TYPES(cls):
        saved = config.load_config(force=True)
        return {
            "required": {
                "视频帧": ("IMAGE", {"tooltip": "视频以多帧 [B,H,W,C] 形式传入"}),
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
                "反推模式": (["复刻", "重构", "分镜解构"],),
                "抽取帧数": ("INT", {"default": 8, "min": 1, "max": 32, "step": 1}),
                "提示词风格": (["详细描述", "简短标签", "英文提示词", "中英混合"],),
                "额外要求": (
                    "STRING",
                    {"multiline": True, "default": "", "placeholder": "选填：补充说明"},
                ),
            },
        }

    def reverse(
        self,
        视频帧,
        API密钥="",
        API网址="",
        模型名称="",
        保存密钥设置=True,
        反推模式="复刻",
        抽取帧数=8,
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
            image_np=视频帧,
            is_video=True,
            max_frames=抽取帧数,
            mode=反推模式,
            style=提示词风格,
            extra_hint=额外要求,
            api_key=API密钥,
            base_url=API网址,
            model=模型名称,
        )
        return (prompt,)
