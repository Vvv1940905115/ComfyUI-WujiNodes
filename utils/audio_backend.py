# -*- coding: utf-8 -*-
"""串接 Meta MusicGen 生成音频。"""

import random

import torch

SAMPLE_RATE = 32000
MODEL_NAME = "facebook/musicgen-melody"

_MODEL_CACHE = {}


def _get_device():
    return "cuda" if torch.cuda.is_available() else "cpu"


def _load_model(model_name=MODEL_NAME):
    """载入并缓存 MusicGen 模型。"""
    if model_name in _MODEL_CACHE:
        return _MODEL_CACHE[model_name]

    from audiocraft.models import MusicGen

    device = _get_device()
    print(f"[WujiNodes] 正在载入 MusicGen 模型：{model_name} (device={device})")
    model = MusicGen.get_pretrained(model_name, device=device)
    _MODEL_CACHE[model_name] = model
    return model


def _silence(duration):
    """产生静音波形作为容错输出。"""
    samples = max(1, int(SAMPLE_RATE * max(1, int(duration))))
    return torch.zeros((1, samples), dtype=torch.float32)


def generate_audio(lyrics, prompt, cfg, steps, seed, duration):
    """生成音频。

    Returns:
        (torch.Tensor[channels, samples], int sample_rate, str log)
    """
    duration = int(duration)
    seed = int(seed) % (2 ** 32)
    full_prompt = f"{prompt}, {str(lyrics)[:200]}".strip(", ").strip()

    logs = [
        "=== 无极音乐人 ===",
        f"模型：{MODEL_NAME}",
        f"提示词：{full_prompt}",
        f"cfg_scale={cfg} / 采样步数={steps} / 种子={seed} / 时长={duration}s",
    ]

    try:
        torch.manual_seed(seed)
        random.seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

        model = _load_model()

        try:
            model.set_cfg_coef(float(cfg))
        except AttributeError:
            logs.append("提示：此版本 audiocraft 无 set_cfg_coef，改由生成参数带入。")

        gen_params = {
            "duration": duration,
            "cfg_coef": float(cfg),
            "top_k": 250,
            "top_p": 0.0,
            "temperature": 1.0,
        }
        try:
            model.set_generation_params(seed=seed, **gen_params)
        except TypeError:
            model.set_generation_params(**gen_params)
            logs.append("提示：此版本 set_generation_params 不支持 seed，已改用全局随机种子。")

        with torch.no_grad():
            wav = model.generate([full_prompt], progress=True)

        audio = wav[0].detach().to("cpu").float()
        if audio.dim() == 1:
            audio = audio.unsqueeze(0)

        sr = int(getattr(model, "sample_rate", SAMPLE_RATE))
        logs.append(
            f"生成成功：shape={tuple(audio.shape)}, sample_rate={sr}"
        )
        return audio, sr, "\n".join(logs)

    except Exception as e:  # noqa: BLE001
        logs.append(f"生成失败：{type(e).__name__}: {e}")
        logs.append("已回传等长静音音频，请确认已安装 audiocraft 并具备足够显存。")
        print("[WujiNodes] " + logs[-2])
        return _silence(duration), SAMPLE_RATE, "\n".join(logs)
