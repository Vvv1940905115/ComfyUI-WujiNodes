# -*- coding: utf-8 -*-
"""插件本地设置管理：保存 API 密钥等信息。

配置文件位置：ComfyUI-WujiNodes/config.json
"""

import json
import os
import threading

_LOCK = threading.Lock()

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PLUGIN_DIR, "config.json")

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"

DEFAULT_CONFIG = {
    "api_key": "",
    "base_url": DEFAULT_BASE_URL,
    "model": DEFAULT_MODEL,
}

_cache = None


def _read_file():
    if not os.path.isfile(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:  # noqa: BLE001
        print(f"[WujiNodes] 配置文件读取失败（将使用默认值）：{e}")
        return {}


def load_config(force=False):
    """载入设置；本地配置文件优先，缺失字段使用内置默认值。"""
    global _cache
    with _LOCK:
        if _cache is not None and not force:
            return dict(_cache)

        cfg = dict(DEFAULT_CONFIG)

        # 本地配置文件优先级最高
        for k, v in _read_file().items():
            if isinstance(v, str) and v.strip():
                cfg[k] = v.strip()

        _cache = cfg
        return dict(cfg)


def save_config(api_key=None, base_url=None, model=None):
    """写入本地配置文件；仅更新有提供且非空的字段。"""
    global _cache
    with _LOCK:
        data = _read_file()
        if api_key and api_key.strip():
            data["api_key"] = api_key.strip()
        if base_url and base_url.strip():
            data["base_url"] = base_url.strip()
        if model and model.strip():
            data["model"] = model.strip()

        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            try:
                os.chmod(CONFIG_PATH, 0o600)
            except OSError:
                pass
            _cache = None
            print(f"[WujiNodes] API 设置已保存至：{CONFIG_PATH}")
            return True
        except Exception as e:  # noqa: BLE001
            print(f"[WujiNodes] 配置文件写入失败：{e}")
            return False


def get_api_key():
    return load_config().get("api_key", "")


def get_base_url():
    return load_config().get("base_url") or DEFAULT_BASE_URL


def get_model():
    return load_config().get("model") or DEFAULT_MODEL


def mask(secret):
    """遮蔽密钥，仅用于日志显示。"""
    if not secret:
        return "(未设置)"
    if len(secret) <= 8:
        return secret[0] + "*" * (len(secret) - 1)
    return f"{secret[:4]}{'*' * 6}{secret[-4:]}"
