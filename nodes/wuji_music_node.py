# -*- coding: utf-8 -*-
"""无极音乐人节点。"""

import random

try:
    from ..utils import audio_backend
except ImportError:  # 直接执行时的回退方案
    from utils import audio_backend

MAX_SEED = 0xFFFFFFFFFFFFFFFF


class WujiMusician:
    CATEGORY = "工坊提示词/音乐"
    RETURN_TYPES = ("AUDIO", "STRING")
    RETURN_NAMES = ("音频波形", "信息日志")
    FUNCTION = "generate_music"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "歌词输入": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "音频描述": ("STRING", {"default": "piano, soft, melody"}),
                "cfg_scale": ("FLOAT", {"default": 2.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "采样步数": ("INT", {"default": 20, "min": 1, "max": 150, "step": 1}),
                "种子": ("INT", {"default": 1025213356904625, "min": 0, "max": MAX_SEED}),
                "control_after_generate": (
                    ["randomize", "fixed", "increment", "decrement"],
                ),
            },
            "optional": {
                "预估时长_秒": ("INT", {"default": 30, "min": 5, "max": 300, "step": 1}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if kwargs.get("control_after_generate") == "randomize":
            return random.random()
        return kwargs.get("种子", 0)

    @staticmethod
    def _resolve_seed(seed, mode):
        seed = int(seed)
        if mode == "randomize":
            return random.randint(0, MAX_SEED)
        if mode == "increment":
            return min(seed + 1, MAX_SEED)
        if mode == "decrement":
            return max(seed - 1, 0)
        return seed

    def generate_music(
        self,
        歌词输入,
        音频描述="piano, soft, melody",
        cfg_scale=2.0,
        采样步数=20,
        种子=1025213356904625,
        control_after_generate="randomize",
        预估时长_秒=30,
    ):
        actual_seed = self._resolve_seed(种子, control_after_generate)

        waveform, sample_rate, log = audio_backend.generate_audio(
            lyrics=歌词输入,
            prompt=音频描述,
            cfg=cfg_scale,
            steps=采样步数,
            seed=actual_seed,
            duration=预估时长_秒,
        )

        # [channels, samples] -> [1, channels, samples]
        if waveform.dim() == 1:
            waveform = waveform.unsqueeze(0)
        if waveform.dim() == 2:
            waveform = waveform.unsqueeze(0)

        audio = {"waveform": waveform, "sample_rate": int(sample_rate)}

        full_log = (
            f"{log}\n"
            f"种子模式={control_after_generate} / 实际使用种子={actual_seed}\n"
            f"输出张量形状={tuple(waveform.shape)}"
        )
        return (audio, full_log)
