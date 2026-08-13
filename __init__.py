# -*- coding: utf-8 -*-
"""ComfyUI-PromptWorkshop：工坊作词师 / 工坊音乐人。"""

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
    "WujiLyricGenerator": "工坊作词师",
    "WujiMusician": "工坊音乐人 (ACE-Step1.5XL)",
    "WujiImageCaption": "工坊图像反推提示词",
    "WujiVideoCaption": "工坊视频反推提示词",
    "WujiPromptTranslator": "工坊提示词翻译",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

_cfg = config.load_config(force=True)
print(
    "\033[95m[ComfyUI-PromptWorkshop]\033[0m 已载入 5 个节点："
    "工坊作词师、工坊音乐人、工坊图像反推提示词、工坊视频反推提示词、工坊提示词翻译 | "
    f"API密钥={config.mask(_cfg.get('api_key', ''))}"
)

# 注册工具栏 API 路由（提示词优化 / 翻译）
try:
    from . import server  # noqa: F401
except Exception as _e:  # noqa: BLE001
    print(f'[ComfyUI-PromptWorkshop] 服务端路由注册失败：{_e}')
