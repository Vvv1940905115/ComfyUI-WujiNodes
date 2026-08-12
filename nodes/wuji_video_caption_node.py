# -*- coding: utf-8 -*-
"""无极视频反推提示词节点。
支持三个输入端口：
  「图像」— 单图 / 多图 [B,H,W,C] 张量（可连 LoadImage 等节点）
  「视频」— 多帧 [B,H,W,C] 张量 或 VHS_VIDEOFORMAT（可直连加载视频节点）
两者均为可选，支持 仅图像、仅视频、图像+视频 三种组合。
"""

import os
import subprocess
import sys
import tempfile

try:
    from ..utils import config, llm_api
except ImportError:  # 直接执行时的回退方案
    from utils import config, llm_api


# ---------------------------------------------------------------
# 帮助函数
# ---------------------------------------------------------------

def _extract_video_path(video_input):
    """从各种视频输入格式中尝试提取视频文件路径。返回路径字符串或 None。"""
    if isinstance(video_input, (tuple, list)) and len(video_input) >= 1:
        src = video_input[0]
        if isinstance(src, dict):
            if src.get("source") == "path" and src.get("path"):
                p = src["path"]
                return p if isinstance(p, str) and os.path.isfile(p) else None
            for key in ("path", "filepath", "file"):
                if key in src and isinstance(src[key], str) and os.path.isfile(src[key]):
                    return src[key]
        for item in video_input:
            if isinstance(item, str) and os.path.isfile(item):
                return item
    if isinstance(video_input, dict):
        for key in ("path", "filepath", "file"):
            if key in video_input and isinstance(video_input[key], str) and os.path.isfile(video_input[key]):
                return video_input[key]
    if isinstance(video_input, str) and os.path.isfile(video_input):
        return video_input
    return None


def _find_ffmpeg():
    """查找可用的 ffmpeg 可执行文件路径。"""
    for exe in ("ffmpeg", "ffmpeg.exe"):
        try:
            r = subprocess.run([exe, "-version"], capture_output=True, timeout=5)
            if r.returncode == 0:
                return exe
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    try:
        import folder_paths
        vhs_dir = os.path.join(folder_paths.base_path, "custom_nodes", "ComfyUI-VideoHelperSuite")
        for root, _dirs, files in os.walk(vhs_dir):
            for f in files:
                if f.lower() in ("ffmpeg.exe", "ffmpeg"):
                    return os.path.join(root, f)
    except Exception:  # noqa: BLE001
        pass
    return None


def _extract_frames_ffmpeg(video_path, max_frames=8, ffmpeg_exe=None):
    """使用 ffmpeg 从视频中均匀抽取 max_frames 帧，返回 [B,H,W,C] numpy 数组（uint8, RGB）。"""
    import numpy as np
    from PIL import Image

    ffmpeg = ffmpeg_exe or _find_ffmpeg()
    if not ffmpeg:
        raise RuntimeError("未找到 ffmpeg，无法从视频文件抽帧，请先使用帧提取节点将视频转为 IMAGE 类型。")

    probe_cmd = [
        ffmpeg, "-i", video_path,
        "-map", "0:v:0", "-c", "copy", "-f", "null", "-",
    ]
    total_frames = None
    try:
        r = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
        for line in r.stderr.splitlines():
            line = line.strip()
            if line.startswith("frame="):
                try:
                    total_frames = int(line.split("frame=")[1].split("fps=")[0].strip())
                except (ValueError, IndexError):
                    pass
    except Exception:  # noqa: BLE001
        total_frames = None

    if not total_frames or total_frames <= 0:
        total_frames = max_frames * 3

    n = min(max_frames, total_frames)
    if n < 1:
        n = 1
    indices = np.linspace(0, total_frames - 1, n).astype(int).tolist()
    select_expr = "+".join([f"eq(n\\,{i})" for i in indices])

    with tempfile.TemporaryDirectory() as tmpdir:
        out_pattern = os.path.join(tmpdir, "frame_%04d.png")
        cmd = [
            ffmpeg, "-i", video_path,
            "-vf", f"select='{select_expr}'",
            "-vsync", "vfr",
            "-frames:v", str(n),
            "-y", out_pattern,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError(f"ffmpeg 抽帧失败：{r.stderr[-500:]}")

        frames = []
        for fname in sorted(os.listdir(tmpdir)):
            if fname.lower().endswith(".png"):
                img = Image.open(os.path.join(tmpdir, fname)).convert("RGB")
                frames.append(np.array(img, dtype=np.uint8))
        if not frames:
            raise RuntimeError("ffmpeg 未能抽取任何帧。")
        return np.stack(frames, axis=0)


def _normalize_video_input(video_input, max_frames=8):
    """将各类视频输入统一为 [B,H,W,C] uint8 numpy 数组。"""
    import numpy as np
    import torch

    if isinstance(video_input, torch.Tensor):
        arr = video_input.detach().cpu().numpy()
        if arr.dtype != np.uint8:
            arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
        else:
            arr = arr.astype(np.uint8)
        if arr.ndim == 3:
            arr = arr[None, ...]
        return arr

    if isinstance(video_input, np.ndarray):
        arr = video_input
        if arr.dtype != np.uint8:
            arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
        else:
            arr = arr.astype(np.uint8)
        if arr.ndim == 3:
            arr = arr[None, ...]
        return arr

    video_path = _extract_video_path(video_input)
    if video_path:
        return _extract_frames_ffmpeg(video_path, max_frames=max_frames)

    if isinstance(video_input, (tuple, list)) and len(video_input) > 0:
        frames = []
        for item in video_input:
            if isinstance(item, torch.Tensor):
                f = item.detach().cpu().numpy()
                if f.dtype != np.uint8:
                    f = np.clip(f * 255.0, 0, 255).astype(np.uint8)
                frames.append(f)
            elif isinstance(item, np.ndarray):
                f = item if item.dtype == np.uint8 else np.clip(item * 255.0, 0, 255).astype(np.uint8)
                frames.append(f)
        if frames:
            return np.stack(frames, axis=0)

    raise TypeError(
        "不支持的视频输入类型：{}。请连接 IMAGE / VHS_VIDEOFORMAT 类型。".format(type(video_input).__name__)
    )


def _normalize_image_input(image_input):
    """将各类单图输入统一为 [B,H,W,C] uint8 numpy 数组。"""
    import numpy as np
    import torch

    if image_input is None:
        return None

    if isinstance(image_input, torch.Tensor):
        arr = image_input.detach().cpu().numpy()
        if arr.dtype != np.uint8:
            arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
        else:
            arr = arr.astype(np.uint8)
        if arr.ndim == 3:
            arr = arr[None, ...]
        return arr

    if isinstance(image_input, np.ndarray):
        arr = image_input
        if arr.dtype != np.uint8:
            arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
        else:
            arr = arr.astype(np.uint8)
        if arr.ndim == 3:
            arr = arr[None, ...]
        return arr

    try:
        from PIL import Image
        if isinstance(image_input, Image.Image):
            arr = np.array(image_input.convert("RGB"), dtype=np.uint8)
            if arr.ndim == 3:
                arr = arr[None, ...]
            return arr
    except ImportError:
        pass

    raise TypeError("不支持的图像输入类型：{}。".format(type(image_input).__name__))


# ---------------------------------------------------------------
# 节点定义
# ---------------------------------------------------------------

class WujiVideoCaption:
    CATEGORY = "提示词工坊 PromptWorkshop/反推"
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
                "反推模式": (["复刻", "重构", "分镜解构"],),
                "抽取帧数": ("INT", {"default": 8, "min": 1, "max": 32, "step": 1}),
                "提示词风格": (["详细描述", "简短标签", "英文提示词", "中英混合"],),
                "额外要求": (
                    "STRING",
                    {"multiline": True, "default": "", "placeholder": "选填：补充说明"},
                ),
            },
            "optional": {
                "图像": (
                    "*",
                    {"tooltip": "可选：单图或多图 [B,H,W,C] 张量（可连 LoadImage 等），与视频二选一或同时使用"},
                ),
                "视频": (
                    "*",
                    {"tooltip": "可选：多帧 [B,H,W,C] 张量 或 VHS_VIDEOFORMAT（可直连加载视频节点），与图像二选一或同时使用"},
                ),
            },
        }

    def reverse(
        self,
        API密钥="",
        API网址="",
        模型名称="",
        保存密钥设置=True,
        反推模式="复刻",
        抽取帧数=8,
        提示词风格="详细描述",
        额外要求="",
        图像=None,
        视频=None,
    ):
        if 保存密钥设置 and (API密钥.strip() or API网址.strip() or 模型名称.strip()):
            config.save_config(
                api_key=API密钥,
                base_url=API网址,
                model=模型名称,
            )

        import numpy as np

        image_frames = None
        video_frames = None

        # 处理图像输入
        try:
            if 图像 is not None:
                image_frames = _normalize_image_input(图像)
        except Exception as e:  # noqa: BLE001
            err_msg = f"（图像输入解析失败：{e}）"
            print(f"[WujiNodes] {err_msg}")
            return (err_msg,)

        # 处理视频输入
        try:
            if 视频 is not None:
                video_frames = _normalize_video_input(视频, max_frames=抽取帧数)
        except Exception as e:  # noqa: BLE001
            err_msg = f"（视频输入解析失败：{e}）"
            print(f"[WujiNodes] {err_msg}")
            return (err_msg,)

        # 合并帧（图像帧在前，视频帧在后）
        parts = []
        if image_frames is not None and image_frames.shape[0] > 0:
            parts.append(image_frames)
        if video_frames is not None and video_frames.shape[0] > 0:
            parts.append(video_frames)

        if not parts:
            return ("（请至少连接「图像」或「视频」其中一个输入端口）",)

        if len(parts) == 1:
            frames_np = parts[0]
        else:
            frames_np = np.concatenate(parts, axis=0)

        prompt = llm_api.reverse_prompt(
            image_np=frames_np,
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
