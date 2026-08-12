# -*- coding: utf-8 -*-
"""无极作词师节点。"""

try:
    from ..utils import config, llm_api
except ImportError:  # 直接执行时的回退方案
    from utils import config, llm_api


class WujiLyricGenerator:
    CATEGORY = "提示词工坊/作词"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("生成歌词",)
    FUNCTION = "generate"

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
                "主题动力源": (
                    "STRING",
                    {"multiline": True, "default": "一位在城市打拼的上班族"},
                ),
                "成品歌词参考": (
                    "STRING",
                    {"multiline": True, "default": "", "placeholder": "选填：贴上参考歌词"},
                ),
                "手动标签": ("STRING", {"default": "孤独, 奋斗, 希望"}),
                "英文标签": ("STRING", {"default": "city, night, dream"}),
                "性别声色": (["女性", "男性", "中性"],),
                "押韵方案": (["自由", "AABB", "ABAB", "AAAA"],),
                "语言选择": (["中文", "英文", "中英混合"],),
            },
            "optional": {
                "进阶_流派": ("STRING", {"default": "流行摇滚"}),
                "进阶_情绪": ("STRING", {"default": "略带沧桑却充满力量"}),
                "进阶_乐器": ("STRING", {"default": "钢琴, 电吉他, 贝斯"}),
                "进阶_BPM": ("INT", {"default": 120, "min": 40, "max": 200, "step": 1}),
                "进阶_拍号": (["4/4", "3/4", "6/8"],),
                "进阶_调式": (["C大调", "A小调", "G大调"],),
                "标签数量": ("INT", {"default": 3, "min": 1, "max": 10, "step": 1}),
            },
        }

    def generate(
        self,
        API密钥="",
        API网址="",
        模型名称="",
        保存密钥设置=True,
        主题动力源="",
        成品歌词参考="",
        手动标签="",
        英文标签="",
        性别声色="中性",
        押韵方案="自由",
        语言选择="中文",
        进阶_流派="流行摇滚",
        进阶_情绪="略带沧桑却充满力量",
        进阶_乐器="钢琴, 电吉他, 贝斯",
        进阶_BPM=120,
        进阶_拍号="4/4",
        进阶_调式="C大调",
        标签数量=3,
    ):
        if 保存密钥设置 and (API密钥.strip() or API网址.strip() or 模型名称.strip()):
            config.save_config(
                api_key=API密钥,
                base_url=API网址,
                model=模型名称,
            )

        lyrics = llm_api.generate_lyrics(
            theme=主题动力源,
            reference_lyrics=成品歌词参考,
            manual_tags=手动标签,
            english_tags=英文标签,
            gender=性别声色,
            rhyme=押韵方案,
            language=语言选择,
            genre=进阶_流派,
            emotion=进阶_情绪,
            instruments=进阶_乐器,
            bpm=进阶_BPM,
            time_signature=进阶_拍号,
            key_mode=进阶_调式,
            tag_count=标签数量,
            api_key=API密钥,
            base_url=API网址,
            model=模型名称,
        )
        return (lyrics,)
