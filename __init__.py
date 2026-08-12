# -*- coding: utf-8 -*-
"""ComfyUI-WujiNodes：无极作词师 / 无极音乐人。"""

from .nodes.wuji_lyric_node import WujiLyricGenerator
from .nodes.wuji_music_node import WujiMusician
from .nodes.wuji_image_caption_node import WujiImageCaption
from .nodes.wuji_video_caption_node import WujiVideoCaption
from .nodes.wuji_translate_node import WujiPromptTranslator
from .utils import config

# 让 ComfyUI 加载 js/ 目录下的前端脚本（wuji_ui.js）
WEB_DIRECTORY = "./js"

NODE_CLASS_MAPPINGS = {
    "WujiLyricGenerator": WujiLyricGenerator,
    "WujiMusician": WujiMusician,
    "WujiImageCaption": WujiImageCaption,
    "WujiVideoCaption": WujiVideoCaption,
    "WujiPromptTranslator": WujiPromptTranslator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WujiLyricGenerator": "无极作词师",
    "WujiMusician": "无极音乐人 (ACE-Step1.5XL)",
    "WujiImageCaption": "无极图像反推提示词",
    "WujiVideoCaption": "无极视频反推提示词",
    "WujiPromptTranslator": "无极提示词翻译",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

_cfg = config.load_config(force=True)
print(
    "\033[95m[ComfyUI-WujiNodes]\033[0m 已载入 5 个节点："
    "无极作词师、无极音乐人、无极图像反推提示词、无极视频反推提示词、无极提示词翻译 | "
    f"API密钥={config.mask(_cfg.get('api_key', ''))}"
)
