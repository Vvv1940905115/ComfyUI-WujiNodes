# -*- coding: utf-8 -*-
"""ComfyUI-WujiNodes：无极作词师 / 无极音乐人。"""

from .nodes.wuji_lyric_node import WujiLyricGenerator
from .nodes.wuji_music_node import WujiMusician
from .nodes.wuji_settings_node import WujiApiSettings
from .nodes.wuji_image_caption_node import WujiImageCaption
from .nodes.wuji_video_caption_node import WujiVideoCaption
from .nodes.wuji_translate_node import WujiPromptTranslator
from .utils import config

NODE_CLASS_MAPPINGS = {
    "WujiApiSettings": WujiApiSettings,
    "WujiLyricGenerator": WujiLyricGenerator,
    "WujiMusician": WujiMusician,
    "WujiImageCaption": WujiImageCaption,
    "WujiVideoCaption": WujiVideoCaption,
    "WujiPromptTranslator": WujiPromptTranslator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WujiApiSettings": "无极 API 设置",
    "WujiLyricGenerator": "无极作词师",
    "WujiMusician": "无极音乐人 (ACE-Step1.5XL)",
    "WujiImageCaption": "无极图像反推提示词",
    "WujiVideoCaption": "无极视频反推提示词",
    "WujiPromptTranslator": "无极提示词翻译",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

_cfg = config.load_config(force=True)
print(
    "\033[95m[ComfyUI-WujiNodes]\033[0m 已载入 6 个节点："
    "无极 API 设置、无极作词师、无极音乐人、无极图像反推提示词、无极视频反推提示词、无极提示词翻译 | "
    f"API密钥={config.mask(_cfg.get('api_key', ''))}"
)
