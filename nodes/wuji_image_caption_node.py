# -*- coding: utf-8 -*-
"""无极图像反推提示词节点。支持外部 IMAGE 连接，也支持节点内直接上传图片。"""

import os

try:
    from ..utils import config, llm_api
except ImportError:  # 直接执行时的回退方案
    from utils import config, llm_api


def _load_image_from_input_dir(filename):
    """从 ComfyUI input 目录加载图片，返回 [H,W,C] uint8 numpy 数组。"""
    try:
        from folder_paths import get_input_directory  # 新版 ComfyUI
    except ImportError:
        from folder_paths import input_directory as get_input_directory  # 旧版兼容

    import numpy as np
    from PIL import Image

    input_dir = get_input_directory() if callable(get_input_directory) else get_input_directory

    # 支持子目录
    path = os.path.join(input_dir, filename)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"input 目录下找不到图片：{filename}")

    img = Image.open(path).convert("RGB")
    return np.array(img, dtype=np.uint8)


def _normalize_image_input(image_input, image_file=""):
    """将各类图像输入统一为 [H,W,C] uint8 numpy 数组。

    支持: torch.Tensor（[H,W,C] 或 [B,H,W,C]）、numpy 数组、PIL Image、文件路径字符串、None。
    """
    if image_input is None and not image_file:
        return None

    import numpy as np

    # 优先级：外部传入的 tensor/ndarray > 内置上传的图片文件
    if image_input is not None:
        # torch.Tensor（ComfyUI 标准 IMAGE: [B,H,W,C] float 0-1）
        try:
            import torch
            if isinstance(image_input, torch.Tensor):
                arr = image_input.detach().cpu().numpy()
                if arr.dtype != np.uint8:
                    arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
                else:
                    arr = arr.astype(np.uint8)
                # 取第一帧（如果是 batch）
                if arr.ndim == 4:
                    arr = arr[0]
                return arr
        except ImportError:
            pass

        # numpy 数组
        if isinstance(image_input, np.ndarray):
            arr = image_input
            if arr.dtype != np.uint8:
                arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
            else:
                arr = arr.astype(np.uint8)
            if arr.ndim == 4:
                arr = arr[0]
            return arr

        # PIL Image
        try:
            from PIL import Image
            if isinstance(image_input, Image.Image):
                return np.array(image_input.convert("RGB"), dtype=np.uint8)
        except ImportError:
            pass

        # 文件路径字符串
        if isinstance(image_input, str) and image_input.strip():
            p = image_input.strip()
            if os.path.isfile(p):
                from PIL import Image
                return np.array(Image.open(p).convert("RGB"), dtype=np.uint8)
            # 可能是 input 目录下的文件名
            try:
                return _load_image_from_input_dir(p)
            except Exception:
                pass

    # 回退：从内置上传的文件加载
    if image_file and image_file.strip():
        try:
            return _load_image_from_input_dir(image_file.strip())
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(f"无法加载上传的图片「{image_file}」：{e}")

    return None


class WujiImageCaption:
    CATEGORY = "无极 Wuji/反推"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("反推提示词",)
    FUNCTION = "reverse"

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
            "optional": {
                "图像": (
                    "*",
                    {"tooltip": "外部连入的 IMAGE 张量（可直接连 LoadImage 等节点）；不连接时请使用下方的内置上传按钮"},
                ),
                "图片文件": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "tooltip": "通过前端上传按钮选择的图片文件名，自动填充",
                    },
                ),
            },
        }

    def reverse(
        self,
        API密钥="",
        API网址="",
        模型名称="",
        保存密钥设置=True,
        扩写模式="通用",
        提示词风格="详细描述",
        额外要求="",
        图像=None,
        图片文件="",
    ):
        if 保存密钥设置 and (API密钥.strip() or API网址.strip() or 模型名称.strip()):
            config.save_config(
                api_key=API密钥,
                base_url=API网址,
                model=模型名称,
            )

        # 统一处理图像输入
        try:
            img_np = _normalize_image_input(图像, 图片文件)
        except Exception as e:  # noqa: BLE001
            err_msg = f"（图片输入解析失败：{e}）"
            print(f"[WujiNodes] {err_msg}")
            return (err_msg,)

        if img_np is None:
            return ("（请连接图像输入或使用内置上传按钮选择图片）",)

        prompt = llm_api.reverse_prompt(
            image_np=img_np,
            is_video=False,
            mode=扩写模式,
            style=提示词风格,
            extra_hint=额外要求,
            api_key=API密钥,
            base_url=API网址,
            model=模型名称,
        )
        return (prompt,)
