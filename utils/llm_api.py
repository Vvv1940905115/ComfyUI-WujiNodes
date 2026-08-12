# -*- coding: utf-8 -*-
"""串接 OpenAI 兼容 API 生成歌词。"""

try:
    from . import config
except ImportError:  # 直接执行时的回退方案
    from utils import config

DEFAULT_BASE_URL = config.DEFAULT_BASE_URL

SYSTEM_PROMPT = (
    "你是一位顶尖的专业作词人，擅长为流行、摇滚、民谣、电子等多种曲风创作歌词。\n"
    "创作要求：\n"
    "1. 严格遵守用户指定的语言、押韵方案、性别声色与情绪。\n"
    "2. 歌词需具备完整结构，使用 [Verse]、[Chorus]、[Bridge]、[Outro] 等标记分段。\n"
    "3. 意象具体、避免空泛口号，句长适合演唱且符合指定 BPM 的节奏感。\n"
    "4. 只输出歌词本文与段落标记，不要输出任何解释、前言或 Markdown 围栏。"
)

FALLBACK_LYRICS = """[Verse 1]
清晨的闹钟敲醒霓虹的残影
我把疲惫折好 塞进西装口袋里
地铁载着沉默 穿过城市的缝隙
每一站都有人 悄悄放弃或继续

[Chorus]
我还在走 在钢铁森林里奔走
把眼泪熬成 明天的理由
就算风很冷 梦还握在手
总有一盏灯 为我留在尽头

[Verse 2]
加班的月光 是唯一的观众
键盘敲出心跳 一下一下很沉重
我不是英雄 只是不肯认输的普通
在破碎的日子 拼出完整的梦

[Bridge]
如果孤独是必经的路
我就把它走成一首歌
如果希望需要代价
我愿意用整个青春交换

[Outro]
天亮了 我还在这里
天亮了 我还没放弃
"""


def _build_user_prompt(
    theme,
    reference_lyrics="",
    manual_tags="",
    english_tags="",
    gender="中性",
    rhyme="自由",
    language="中文",
    genre="",
    emotion="",
    instruments="",
    bpm=120,
    time_signature="4/4",
    key_mode="",
    tag_count=3,
):
    """组装结构化的用户提示词。"""
    lines = [
        "请依照以下设置创作一首完整的歌曲歌词。",
        "",
        "【核心设置】",
        f"- 主题动力源：{theme}",
        f"- 语言选择：{language}",
        f"- 性别声色：{gender}（歌词的叙事口吻与音域需符合此设置）",
        f"- 押韵方案：{rhyme}",
        "",
        "【风格设置】",
        f"- 流派：{genre or '不限'}",
        f"- 情绪：{emotion or '自然真挚'}",
        f"- 乐器编制：{instruments or '不限'}",
        f"- BPM：{bpm}",
        f"- 拍号：{time_signature}",
        f"- 调式：{key_mode or '不限'}",
        "",
        "【标签参考】",
        f"- 中文标签：{manual_tags or '无'}",
        f"- 英文标签：{english_tags or '无'}",
        f"- 标签数量建议：意象请围绕其中约 {tag_count} 个核心标签展开",
    ]

    if reference_lyrics and reference_lyrics.strip():
        lines += [
            "",
            "【成品歌词参考】（仅参考其风格与句式，严禁抄袭原句）",
            reference_lyrics.strip(),
        ]

    if rhyme != "自由":
        lines += ["", f"【押韵硬性要求】主歌与副歌的句尾请严格遵循 {rhyme} 的韵脚排列。"]

    lines += [
        "",
        "【输出格式】",
        "直接输出歌词，使用 [Verse 1] / [Chorus] / [Verse 2] / [Bridge] / [Outro] 分段，不要任何额外说明。",
    ]
    return "\n".join(lines)


def _call_openai(system_prompt, user_prompt, api_key, base_url, model):
    """优先使用 openai SDK，失败时回退 requests。"""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key, base_url=base_url)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.9,
            max_tokens=1500,
        )
        return resp.choices[0].message.content
    except ImportError:
        import requests

        url = base_url.rstrip("/") + "/chat/completions"
        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.9,
                "max_tokens": 1500,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


def _image_to_data_uri(image_np):
    """将 [H, W, C] 0-255 numpy 数组编码为 PNG data URI。"""
    import base64
    import io

    from PIL import Image

    img = Image.fromarray(image_np.astype("uint8"), "RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _call_openai_vision(system_prompt, user_text, image_data_uris, api_key, base_url, model):
    """多模态调用：向支持视觉的模型发送文本 + 一或多张图片。"""
    content = [{"type": "text", "text": user_text}]
    for uri in image_data_uris:
        content.append({"type": "image_url", "image_url": {"url": uri}})

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key, base_url=base_url)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ],
            temperature=0.6,
            max_tokens=1200,
        )
        return resp.choices[0].message.content
    except ImportError:
        import requests

        url = base_url.rstrip("/") + "/chat/completions"
        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content},
                ],
                "temperature": 0.6,
                "max_tokens": 1200,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


def reverse_prompt(
    image_np,
    is_video=False,
    max_frames=8,
    mode="通用",
    style="详细描述",
    extra_hint="",
    api_key="",
    base_url="",
    model="",
):
    """图像/视频反推提示词；任何异常皆回退到占位文本。

    image_np 为 [B, H, W, C]（视频多帧）或 [H, W, C]（单图）的 numpy 数组。
    api_key / base_url / model 若未传入，将自动读取插件本地设置 config.json。
    """
    import numpy as np

    api_key = (api_key or "").strip() or config.get_api_key()
    base_url = (base_url or "").strip() or config.get_base_url()
    model = (model or "").strip() or config.get_model()

    arr = np.asarray(image_np)
    if arr.ndim == 3:  # 单图 [H, W, C] -> 视为 1 帧
        arr = arr[None, ...]
    frames = arr
    if is_video and frames.shape[0] > max_frames:
        idx = np.linspace(0, frames.shape[0] - 1, max_frames).astype(int)
        frames = frames[idx]

    if not api_key:
        print("[WujiNodes] 尚未设置 API 密钥，请在节点的 API密钥 字段填入，无法反推提示词。")
        return "（尚未设置 API 密钥，无法反推提示词）"

    try:
        data_uris = [_image_to_data_uri(f) for f in frames]
    except Exception as e:  # noqa: BLE001
        print(f"[WujiNodes] 图像编码失败：{e}")
        return "（图像编码失败，无法反推提示词）"

    if is_video:
        if mode == "分镜解构":
            system = (
                "你是一位专业的视频分镜解构大师。用户会提供同一视频中抽取的多帧画面，"
                "请将这些画面拆解为一个个分镜（shot），逐镜描述其画面构成、主体动作、"
                "镜头运动、景别、场景与光影风格，并给出可复用的分镜提示词。\n"
                "要求：\n"
                "1. 按时间顺序（帧序）逐镜编号输出，如 [Shot 1]、[Shot 2]…\n"
                "2. 每镜包含：画面描述 + 镜头运动/景别 + 一句可直接用于生成的提示词。\n"
                "3. 语言与风格遵循用户指定的要求，不要输出无关解释。"
            )
            user_text = (
                f"以下是某视频按顺序抽取的 {len(data_uris)} 帧画面，请作为分镜解构大师"
                f"逐镜拆解并给出分镜提示词。\n提示词风格：{style}。"
            )
        elif mode == "重构":
            system = (
                "你是一位专业的视频内容再创作助手。用户会提供同一视频中抽取的多帧画面，"
                "请理解其主题、风格与情绪，但进行『重构』——在保留核心氛围与风格的前提下，"
                "重新设计镜头、构图与叙事节奏，反推出一份可生成『同风格新视频』的提示词。\n"
                "要求：\n"
                "1. 不必逐帧复刻，重在提炼风格与情绪并给出更具创作性的提示词。\n"
                "2. 描述主体、动作、镜头运动、场景、光照与色彩风格的整体方向。\n"
                "3. 语言与风格遵循用户指定的要求，直接输出提示词，不要解释。"
            )
            user_text = (
                f"以下是某视频抽取的 {len(data_uris)} 帧画面，请基于其风格与情绪进行重构，"
                f"反推一份可生成同风格新视频的提示词。\n提示词风格：{style}。"
            )
        else:  # 复刻
            system = (
                "你是一位专业的视频内容分析助手。用户会提供同一视频中抽取的多帧画面，"
                "请综合这些帧的内容，反推出用于『精确复刻』该视频的提示词（prompt）。\n"
                "要求：\n"
                "1. 描述画面主体、动作、镜头运动、场景、光照与色彩风格。\n"
                "2. 指出跨帧保持一致的要素与随时间变化的要素。\n"
                "3. 语言与风格遵循用户指定的要求，直接输出提示词，不要解释。"
            )
            user_text = (
                f"以下是某视频抽取的 {len(data_uris)} 帧画面，请反推可精确复刻该视频的"
                f"生成提示词。\n提示词风格：{style}。"
            )
    else:
        _image_modes = {
            "通用": (
                "你是一位专业的图像内容分析助手。用户会提供一张图片，"
                "请反推出用于生成该图片的提示词（prompt），并对画面做均衡、通用的扩写。\n"
                "要求：\n"
                "1. 描述画面主体、构图、光照、色彩、材质与风格。\n"
                "2. 语言与风格遵循用户指定的要求，直接输出提示词，不要解释。"
            ),
            "人像大师": (
                "你是一位专业的人像摄影大师。请分析这张人像图片，"
                "反推可用于生成同等质量人像的提示词，并重点扩写人物特征、"
                "面部神态、肤质、发型、妆容、身材与姿态、服装材质与镜头景别。\n"
                "要求：\n"
                "1. 详细描述人物五官、表情、情绪与镜头距离（特写/半身/全身）。\n"
                "2. 补充光影、虚化背景与画质细节（如 8k、raw 照片质感）。\n"
                "3. 直接输出提示词，不要解释。"
            ),
            "Tags 风格": (
                "你是一位以标签（tags）方式描述图像的助手。请分析这张图片，"
                "反推其生成提示词，并以『逗号分隔的标签列表』风格输出，"
                "前段为英文 tag、后段可附中文说明。\n"
                "要求：\n"
                "1. 输出形如：subject, style, lighting, camera, mood, ...（逗号分隔，无编号）。\n"
                "2. 标签精炼、可被主流图像模型直接消费。\n"
                "3. 直接输出标签，不要解释。"
            ),
            "电影镜头视觉": (
                "你是一位电影感镜头设计专家。请分析这张图片，"
                "反推其生成提示词，并重点扩写电影化运镜、景别、焦段、"
                "色调与叙事氛围（如 anamorphic、cinematic、35mm film）。\n"
                "要求：\n"
                "1. 描述镜头类型（远景/中景/特写）、焦段与景深、胶片颗粒与色温。\n"
                "2. 强调电影海报/电影剧照般的视觉语言。\n"
                "3. 直接输出提示词，不要解释。"
            ),
            "光影质感视觉": (
                "你是一位专注于光影与材质的视觉专家。请分析这张图片，"
                "反推其生成提示词，并重点扩写光照方向、光比、阴影、"
                "反射与各类表面材质质感（金属/玻璃/织物/皮肤等）。\n"
                "要求：\n"
                "1. 描述主光、补光、轮廓光与整体光比，注明高光与阴影处理。\n"
                "2. 强调材质细节与真实感渲染（如 volumetric light、subsurface scattering）。\n"
                "3. 直接输出提示词，不要解释。"
            ),
            "氛围场景视觉": (
                "你是一位场景氛围设计师。请分析这张图片，"
                "反推其生成提示词，并重点扩写环境、天气、时间、"
                "空间纵深与整体情绪氛围（如 moody、atmospheric、dreamy）。\n"
                "要求：\n"
                "1. 描述场景类别、天气、时段、空气透视与情绪基调。\n"
                "2. 强调环境叙事与氛围渲染。\n"
                "3. 直接输出提示词，不要解释。"
            ),
            "美学构图视觉": (
                "你是一位构图与美学指导。请分析这张图片，"
                "反推其生成提示词，并重点扩写构图法则、线条、"
                "平衡、留白与色彩美学（如 rule of thirds、golden ratio、negative space）。\n"
                "要求：\n"
                "1. 描述构图方式、视觉引导线、主体位置与色彩搭配。\n"
                "2. 强调形式美感与版面节奏。\n"
                "3. 直接输出提示词，不要解释。"
            ),
        }
        system = _image_modes.get(mode, _image_modes["通用"])
        if mode == "Tags 风格":
            user_text = f"请按『逗号分隔标签』风格反推这张图片的生成提示词。\n提示词风格：{style}。"
        else:
            user_text = f"请使用『{mode}』视角扩写并反推这张图片的生成提示词。\n提示词风格：{style}。"

    if extra_hint and extra_hint.strip():
        user_text += f"\n额外要求：{extra_hint.strip()}"

    try:
        print(f"[WujiNodes] 反推提示词 调用 {base_url} / model={model} / key={config.mask(api_key)}")
        text = _call_openai_vision(system, user_text, data_uris, api_key, base_url, model)
        if not text or not text.strip():
            raise ValueError("API 返回空内容")
        return text.strip()
    except Exception as e:  # noqa: BLE001
        print(f"[WujiNodes] 反推提示词 API 调用失败：{e}")
        return "（反推提示词 API 调用失败，请检查密钥与模型是否支持视觉）"


def translate_prompt(
    text,
    target_lang="英文",
    source_lang="自动检测",
    keep_tags=False,
    extra_hint="",
    api_key="",
    base_url="",
    model="",
):
    """提示词翻译；任何异常皆回退到原文。

    api_key / base_url / model 若未传入，将自动读取插件本地设置 config.json。
    """
    api_key = (api_key or "").strip() or config.get_api_key()
    base_url = (base_url or "").strip() or config.get_base_url()
    model = (model or "").strip() or config.get_model()

    text = (text or "").strip()
    if not text:
        return ""

    if not api_key:
        print("[WujiNodes] 尚未设置 API 密钥，请在节点的 API密钥 字段填入，无法翻译。")
        return text

    system = (
        "你是一位专业的 AI 绘画提示词翻译专家，精通中英文及常见标签（tag）风格。\n"
        "请将用户给出的提示词翻译为目标语言，并保持可直接用于图像/视频生成模型的格式。\n"
        "要求：\n"
        "1. 忠实原意，不增删主体与风格信息；保留专业术语与模型惯用表达。\n"
        "2. 若原文是逗号分隔的标签（tags），译文也保持标签列表格式。\n"
        "3. 直接输出翻译结果，不要任何解释或 Markdown 围栏。"
    )

    tag_note = "保持逗号分隔的标签（tag）列表格式。" if keep_tags else "按自然语言或标签格式均可，以最适合目标语言模型为准。"
    user_text = (
        f"请将以下提示词翻译为「{target_lang}」"
        f"（源语言：{source_lang}）。{tag_note}\n"
        f"待翻译内容：\n{text}"
    )
    if extra_hint and extra_hint.strip():
        user_text += f"\n额外要求：{extra_hint.strip()}"

    try:
        print(f"[WujiNodes] 提示词翻译 调用 {base_url} / model={model} / key={config.mask(api_key)}")
        result = _call_openai(system, user_text, api_key, base_url, model)
        if not result or not result.strip():
            raise ValueError("API 返回空内容")
        return result.strip()
    except Exception as e:  # noqa: BLE001
        print(f"[WujiNodes] 提示词翻译 API 调用失败：{e}，返回原文。")
        return text


def generate_lyrics(
    theme,
    reference_lyrics="",
    manual_tags="",
    english_tags="",
    gender="中性",
    rhyme="自由",
    language="中文",
    genre="",
    emotion="",
    instruments="",
    bpm=120,
    time_signature="4/4",
    key_mode="",
    tag_count=3,
    api_key="",
    base_url="",
    model="",
):
    """生成歌词；任何异常皆回传默认示范歌词。

    api_key / base_url / model 若未传入，将自动读取插件本地设置 config.json。
    """
    api_key = (api_key or "").strip() or config.get_api_key()
    base_url = (base_url or "").strip() or config.get_base_url()
    model = (model or "").strip() or config.get_model()

    user_prompt = _build_user_prompt(
        theme=theme,
        reference_lyrics=reference_lyrics,
        manual_tags=manual_tags,
        english_tags=english_tags,
        gender=gender,
        rhyme=rhyme,
        language=language,
        genre=genre,
        emotion=emotion,
        instruments=instruments,
        bpm=bpm,
        time_signature=time_signature,
        key_mode=key_mode,
        tag_count=tag_count,
    )

    if not api_key:
        print("[WujiNodes] 尚未设置 API 密钥，请在「工坊作词师」节点的 API密钥 字段填入，改用默认示范歌词。")
        return FALLBACK_LYRICS

    try:
        print(f"[WujiNodes] 调用 {base_url} / model={model} / key={config.mask(api_key)}")
        text = _call_openai(SYSTEM_PROMPT, user_prompt, api_key, base_url, model)
        if not text or not text.strip():
            raise ValueError("API 返回空内容")
        return text.strip()
    except Exception as e:  # noqa: BLE001
        print(f"[WujiNodes] 歌词 API 调用失败：{e}，改用默认示范歌词。")
        return FALLBACK_LYRICS
