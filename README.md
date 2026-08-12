# ComfyUI-WujiNodes（无极节点）

ComfyUI 自定义节点插件，提供 AI 歌词生成、AI 音乐生成、图像/视频提示词反推与提示词翻译功能。

![节点数](https://img.shields.io/badge/节点-6个-purple)
![许可证](https://img.shields.io/badge/license-MIT-green)

---

## 目录

- [功能简介](#功能简介)
- [环境要求](#环境要求)
- [安装教程（详细步骤）](#安装教程详细步骤)
  - [第一步：确认你的 ComfyUI 安装了](#第一步确认你的-comfyui-安装了)
  - [第二步：获取插件文件](#第二步获取插件文件)
  - [第三步：确认 Python 解释器路径](#第三步确认-python-解释器路径)
  - [第四步：安装依赖](#第四步安装依赖)
  - [第五步：重启 ComfyUI 并验证](#第五步重启-comfyui-并验证)
  - [依赖未安装 / 缺失处理](#依赖未安装--缺失处理)
- [配置 API 密钥](#配置-api-密钥)
  - [方式一：通过节点界面配置（推荐）](#方式一通过节点界面配置推荐)
  - [使用第三方 API 代理](#使用第三方-api-代理)
  - [首次快速上手流程](#首次快速上手流程)
- [节点说明](#节点说明)
  - [无极 API 设置](#无极-api-设置)
  - [无极作词师](#无极作词师)
  - [无极音乐人](#无极音乐人)
  - [无极图像反推提示词](#无极图像反推提示词)
  - [无极视频反推提示词](#无极视频反推提示词)
  - [无极提示词翻译](#无极提示词翻译)
- [常见问题](#常见问题)
- [项目结构](#项目结构)

---

## 功能简介

| 节点 | 功能 | 依赖 |
|------|------|------|
| 无极 API 设置 | 统一管理 OpenAI API 密钥与模型配置 | 无 |
| 无极作词师 | 调用 LLM 生成结构化歌词 | `openai` 或 `requests` |
| 无极音乐人 | 根据歌词 + 文本描述生成音频 | `audiocraft`（可选） |
| 无极图像反推提示词 | 调用视觉模型反推图片的生成提示词 | `openai` 或 `requests` |
| 无极视频反推提示词 | 抽帧后调用视觉模型反推视频的生成提示词 | `openai` 或 `requests` |
| 无极提示词翻译 | 将提示词在多种语言间互译，便于跨模型使用 | `openai` 或 `requests` |

> **注意**：「无极音乐人」节点依赖 Meta 的 `audiocraft` 库，该库在 Windows 便携版 Python 上安装可能需要额外编译工具。该节点即使未安装 audiocraft 也不会导致 ComfyUI 崩溃，执行时会返回静音及错误提示。

---

## 环境要求

- **ComfyUI** 已安装并能正常运行
- **Python 3.10+**（ComfyUI 自带的嵌入式 Python 通常已满足）
- **调用 AI 功能**：需要一个可用的 OpenAI 兼容 API（OpenAI / 第三方代理均可）

---

## 安装教程（详细步骤）

> 下面每一步都可独立执行。如果某一步已经做完（例如 ComfyUI 已经在跑），可以跳过。

### 第一步：确认你的 ComfyUI 安装了

先确认 ComfyUI 能正常启动、能打开 Web 界面。如果还没装 ComfyUI，请先安装并验证可运行，再回来装本插件。

记下你的 ComfyUI 根目录，后面用得到。常见位置举例：

```
D:\Ai\ComfyUI\ComfyUI\
```

插件必须放进根目录下的 `custom_nodes` 文件夹：

```
ComfyUI\
└── custom_nodes\
    └── ComfyUI-WujiNodes\   ← 插件放这里
```

### 第二步：获取插件文件

**方式 A：Git 克隆（推荐，便于后续更新）**

1. 打开命令行（PowerShell 或 CMD），进入 ComfyUI 的 `custom_nodes` 目录：

   ```powershell
   cd D:\Ai\ComfyUI\ComfyUI\custom_nodes
   ```

   > 把路径换成你实际的 ComfyUI 安装目录。

2. 克隆仓库：

   ```powershell
   git clone https://github.com/Vvv1940905115/ComfyUI-WujiNodes.git
   ```

**方式 B：手动下载 ZIP**

1. 在 GitHub 页面点击「Code → Download ZIP」，解压得到 `ComfyUI-WujiNodes` 文件夹
2. 将整个文件夹复制到 `ComfyUI\custom_nodes\` 下，最终路径为：

   ```
   ComfyUI\custom_nodes\ComfyUI-WujiNodes\
   ```

   > 注意文件夹名必须是 `ComfyUI-WujiNodes`，且**不能包含额外空格**，否则 ComfyUI 可能不识别。

### 第三步：确认 Python 解释器路径

这是最容易踩坑的一步。插件依赖必须装到「运行 ComfyUI 的那个 Python」里，装错 Python 等于没装。

**先找到 Python 解释器：**

```powershell
# 便携版 ComfyUI：通常在根目录下的 python_embeded 文件夹
dir D:\Ai\ComfyUI\ComfyUI\python_embeded\python.exe

# 若上面报「找不到路径」，逐个试：
dir D:\Ai\ComfyUI\ComfyUI\python_embeded\
dir D:\Ai\ComfyUI\ComfyUI\python_embedded\   # 注意也可能是 embedded（多一个 d）
```

如果你是用系统 Python / venv 装的 ComfyUI，直接查：

```powershell
where python
python --version
```

**记下你的 Python 路径，二选一：**

| 类型 | 调用方式 |
|------|----------|
| 便携版（找到 `python_embeded\python.exe`） | `D:\Ai\ComfyUI\ComfyUI\python_embeded\python.exe` |
| 系统 / venv Python | 直接用 `python` 或 `pip` 命令 |

> 小技巧：如果你的命令行当前已经在插件目录（形如 `...\custom_nodes\ComfyUI-WujiNodes>`），可用相对路径：
> `..\..\..\python_embeded\python.exe`（从插件目录往上 3 级即 ComfyUI 根目录）。

### 第四步：安装依赖

进入插件目录后执行。**务必用第三步确认的 Python**：

```powershell
# 先进入插件目录（如果还没进）
cd D:\Ai\ComfyUI\ComfyUI\custom_nodes\ComfyUI-WujiNodes

# 便携版 ComfyUI：用完整路径（替换成你实际的 python.exe 路径）
D:\Ai\ComfyUI\ComfyUI\python_embeded\python.exe -m pip install -r requirements.txt

# 或者用相对路径（当前已在插件目录时）
..\..\..\python_embeded\python.exe -m pip install -r requirements.txt

# 系统 / venv Python 安装的 ComfyUI：
pip install -r requirements.txt
```

`requirements.txt` 默认只包含必需依赖（`torch` / `torchaudio` / `numpy` / `Pillow` / `openai` / `requests`）。`audiocraft` 与 `transformers` 已注释为**可选**，不会自动安装，避免 Windows / Python 3.13 下编译失败卡住安装。

看到 `Successfully installed ...` 即代表完成。

### 第五步：重启 ComfyUI 并验证

1. **完全重启 ComfyUI**（关闭再重新运行 `run_nvidia_gpu.bat` / 启动脚本，不是只刷新网页）
2. 查看启动日志，应该能看到：

   ```
   [ComfyUI-WujiNodes] 已载入 6 个节点：无极 API 设置、无极作词师、无极音乐人、无极图像反推提示词、无极视频反推提示词、无极提示词翻译 | API密钥=(未设置)
   ```

3. 在 ComfyUI 右侧节点菜单「**无极 Wuji**」分类下能找到全部 6 个节点，即安装成功。

### 依赖未安装 / 缺失处理

如果启动后报错提示缺少某个 Python 包，或某些节点功能不可用，请按需补装依赖。

**1. 确定 Python 解释器**（见上文「第三步」）

**2. 一键安装全部依赖**

```powershell
# 便携版 ComfyUI
..\..\..\python_embeded\python.exe -m pip install -r requirements.txt

# 标准 pip 安装的 ComfyUI
pip install -r requirements.txt
```

**3. 单独安装某个缺失的包**

若只需补装个别包（例如本地没有 `Pillow` 导致图像反推节点无法编码图片）：

```powershell
# 便携版
..\..\..\python_embeded\python.exe -m pip install Pillow

# 标准 pip
pip install Pillow
```

常用依赖对照：

| 包名 | 用途 | 缺失时的表现 |
|------|------|--------------|
| `torch` / `torchaudio` | ComfyUI 基础运行环境 | 整个 ComfyUI 无法运行（通常由 ComfyUI 自身提供） |
| `Pillow` | 图像编码（图像/视频反推节点） | 反推节点报「图像编码失败」 |
| `openai` | 调用 LLM / 视觉模型（优先） | 自动回退到 `requests`，一般不影响 |
| `requests` | 调用 LLM / 视觉模型（回退） | 两者皆无时 API 调用失败 |
| `audiocraft` | 无极音乐人节点生成音频（可选） | 缺失时该节点安全返回静音波形，不崩溃 |
| `transformers` | 部分后端可选依赖（可选） | 非必需 |

**4. Windows 安装 `audiocraft` 的特别说明（可选）**

`audiocraft` 在 Windows 上需要 MSVC 编译工具，且在 Python 3.13 下极易编译失败。若你需要「无极音乐人」真正出声：

1. **推荐**：把 ComfyUI 换到 **Python 3.10 或 3.11** 的便携版环境，再安装
2. 安装 [Microsoft C++ 生成工具](https://visualstudio.microsoft.com/zh-hans/visual-cpp-build-tools/)
3. 在该 Python 下执行：

   ```powershell
   python.exe -m pip install audiocraft
   ```

即使不装，`无极音乐人` 节点也不会导致 ComfyUI 崩溃，仅返回静音与错误日志。

**5. 验证依赖已就绪**

```powershell
python -c "import PIL, openai; print('Pillow & openai OK')"
```

安装完成后**重启 ComfyUI** 使依赖生效。

---

## 配置 API 密钥

插件所有 AI 功能都需要一个 OpenAI 兼容的 API 密钥。本插件支持三种使用场景，但**只推荐方式一**（方式二/方式三已移除）。

### 方式一：通过节点界面配置（推荐）

在 ComfyUI 工作流中：

1. 添加「**无极 API 设置**」节点
2. 填写以下字段：

   | 字段 | 说明 | 默认值 |
   |------|------|--------|
   | API密钥 | 你的 OpenAI 格式 API Key | 空 |
   | API网址 | API 请求地址 | `https://api.openai.com/v1` |
   | 模型名称 | 使用的模型名称 | `gpt-4o-mini` |

3. **按 Ctrl+Enter 执行节点**，密钥即自动保存到 `config.json`。

> 密钥会被保存在插件目录下的 `config.json` 文件中（仅本地），日志输出时会自动遮蔽（如 `sk-1******cdef`）。

### 使用第三方 API 代理

插件支持任意兼容 OpenAI Chat Completions 格式的 API，只需修改「API网址」与「模型名称」即可。例如：

| 服务商 | API网址 | 模型名称示例 |
|--------|---------|--------------|
| OpenAI（官方） | `https://api.openai.com/v1` | `gpt-4o-mini` |
| 国内中转代理 | 填入你的代理地址 | 按代理说明 |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b` |
| 其他兼容服务 | 填入对应的 `/v1` 端点 | 按服务商说明 |

> **图像/视频反推必须用支持视觉的模型**（如 `gpt-4o`）。默认的 `gpt-4o-mini` 在部分服务商处不支持视觉，会导致调用失败。翻译、作词用 `gpt-4o-mini` 即可。

### 首次快速上手流程

装好插件后，最快的体验路径：

1. **配密钥**：拖入「无极 API 设置」节点 → 填 API密钥 / API网址 / 模型名称 → 执行（Ctrl+Enter）。此后其他节点会自动读取，无需重复填。
2. **试作词**：拖入「无极作词师」→ 填「主题动力源」→ 执行，右侧「生成歌词」即出歌词。
3. **试图像反推**：拖入「无极图像反推提示词」→ 连接一张图片 → 选「扩写模式」→ 执行，得到提示词文本。
4. **试翻译**：把上一步的提示词连入「无极提示词翻译」→ 目标语言选「英文」→ 执行，得到英文 tag。

---

## 节点说明

### 无极 API 设置

用于集中管理 API 密钥配置。运行后密钥保存到本地配置文件中，其他节点（如作词师）可自动读取，无需每次填入。

| 参数 | 类型 | 说明 |
|------|------|------|
| API密钥 | STRING | OpenAI 格式 API Key |
| API网址 | STRING | API 基础 URL |
| 模型名称 | STRING | 模型 ID |
| 设置状态 | STRING（输出） | 显示保存状态 |

### 无极作词师

调用 LLM 生成包含 Verse / Chorus / Bridge / Outro 结构的完整歌词。

**必填参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| API密钥 | STRING | 自动读取 | 未设置时需手动填入 |
| API网址 | STRING | `https://api.openai.com/v1` | |
| 模型名称 | STRING | `gpt-4o-mini` | |
| 保存密钥设置 | BOOLEAN | √ | 是否自动保存密钥 |
| 主题动力源 | STRING | （预设） | 歌词主题描述 |
| 成品歌词参考 | STRING（多行） | 空 | 参考歌词样式 |
| 手动标签 | STRING | `孤独, 奋斗, 希望` | 中文关键词 |
| 英文标签 | STRING | `city, night, dream` | 英文关键词 |
| 性别声色 | 下拉 | `中性` | 女性/男性/中性 |
| 押韵方案 | 下拉 | `自由` | AABB/ABAB/AAAA/自由 |
| 语言选择 | 下拉 | `中文` | 中文/英文/中英混合 |

**可选参数：**

| 参数 | 类型 | 默认值 |
|------|------|--------|
| 进阶_流派 | STRING | `流行摇滚` |
| 进阶_情绪 | STRING | `略带沧桑却充满力量` |
| 进阶_乐器 | STRING | `钢琴, 电吉他, 贝斯` |
| 进阶_BPM | INT | `120` (40-200) |
| 进阶_拍号 | 下拉 | `4/4` |
| 进阶_调式 | 下拉 | `C大调` |
| 标签数量 | INT | `3` (1-10) |

### 无极音乐人

接收歌词文本和音频描述，调用 MusicGen 模型生成音频。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| 歌词输入 | STRING（强制输入） | - | 连接作词师输出 |
| 音频描述 | STRING | `piano, soft, melody` | 风格提示词 |
| cfg_scale | FLOAT | `2.0` (0-10) | 引导强度 |
| 采样步数 | INT | `20` (1-150) | 采样步数 |
| 种子 | INT | 随机 | 随机种子 |
| control_after_generate | 下拉 | `randomize` | 种子行为 |
| 预估时长_秒 | INT（可选） | `30` (5-300) | 音频时长 |

**输出：**

- `音频波形` - AUDIO 类型，可连接音频播放节点
- `信息日志` - 生成详情日志

> **已知限制**：当前版本使用 Meta MusicGen 模型而非 ACE-Step1.5XL（节点名称仅为临时标识）。如需安装 `audiocraft` 依赖，Windows 用户建议先安装 C++ 编译工具。该节点缺失依赖时不会导致 ComfyUI 报错，会安全返回静音波形。

### 无极图像反推提示词

调用支持视觉的模型（如 GPT-4o、Gemini 等兼容 `/chat/completions` 的多模态模型），根据输入图片反推其生成提示词。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| 图像 | IMAGE（强制输入） | - | 连接图像加载/预览节点 |
| API密钥 | STRING | 自动读取 | 未设置时需手动填入 |
| API网址 | STRING | `https://api.openai.com/v1` | |
| 模型名称 | STRING | `gpt-4o-mini` | 需使用支持视觉的模型 |
| 保存密钥设置 | BOOLEAN | √ | 是否自动保存密钥 |
| 扩写模式 | 下拉 | `通用` | 见下方扩写模式说明 |
| 提示词风格 | 下拉 | `详细描述` | 详细描述/简短标签/英文提示词/中英混合 |
| 额外要求 | STRING（多行） | 空 | 对反推的补充说明 |

**输出：**

- `反推提示词` - STRING 类型，可直接连接其他图像生成节点的提示词输入

**扩写模式说明：**

| 模式 | 侧重点 |
|------|--------|
| 通用 | 均衡描述主体、构图、光照、色彩与风格 |
| 人像大师 | 人物五官、神态、肤质、发型妆容、景别与画质细节 |
| Tags 风格 | 以逗号分隔的标签列表输出，可直接被图像模型消费 |
| 电影镜头视觉 | 运镜、景别、焦段、胶片色调与电影化叙事氛围 |
| 光影质感视觉 | 光照方向、光比、阴影、反射与材质真实感渲染 |
| 氛围场景视觉 | 环境、天气、时段、空间纵深与整体情绪氛围 |
| 美学构图视觉 | 构图法则、视觉引导线、留白与色彩美学 |

> **注意**：反推功能依赖视觉模型，请将「模型名称」设为支持图像输入的模型（如 `gpt-4o`），默认的 `gpt-4o-mini` 在部分服务商处不支持视觉。

### 无极视频反推提示词

将输入视频（以多帧 `[B,H,W,C]` 张量形式）按「抽取帧数」均匀抽帧，连同多帧画面一并发送给视觉模型，反推视频生成提示词（含主体、动作、镜头运动与风格）。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| 视频帧 | IMAGE（强制输入） | - | 连接视频加载节点（多帧） |
| API密钥 | STRING | 自动读取 | 未设置时需手动填入 |
| API网址 | STRING | `https://api.openai.com/v1` | |
| 模型名称 | STRING | `gpt-4o-mini` | 需使用支持视觉的模型 |
| 保存密钥设置 | BOOLEAN | √ | 是否自动保存密钥 |
| 反推模式 | 下拉 | `复刻` | 复刻 / 重构 / 分镜解构 |
| 抽取帧数 | INT | `8` (1-32) | 送审的帧数上限 |
| 提示词风格 | 下拉 | `详细描述` | 详细描述/简短标签/英文提示词/中英混合 |
| 额外要求 | STRING（多行） | 空 | 对反推的补充说明 |

**输出：**

- `反推提示词` - STRING 类型，可直接连接视频生成节点的提示词输入

**反推模式说明：**

| 模式 | 行为 |
|------|------|
| 复刻 | 精确还原原视频，输出可用于 1:1 复刻的生成提示词 |
| 重构 | 保留原视频风格与情绪，重新设计镜头与叙事，输出同风格新视频提示词 |
| 分镜解构 | 逐镜拆解视频，按帧序输出每镜的画面描述、镜头运动与可复用分镜提示词 |

> **注意**：反推功能依赖视觉模型，请将「模型名称」设为支持图像输入的模型（如 `gpt-4o`），默认的 `gpt-4o-mini` 在部分服务商处不支持视觉。

### 无极提示词翻译

将已有提示词在多种语言之间互译（如把中文扩写结果译为英文 tags 供 Stable Diffusion 使用），便于跨模型复用。复用「无极 API 设置」的密钥配置。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| 提示词 | STRING（强制输入） | - | 连接上游反推/作词节点输出 |
| API密钥 | STRING | 自动读取 | 未设置时需手动填入 |
| API网址 | STRING | `https://api.openai.com/v1` | |
| 模型名称 | STRING | `gpt-4o-mini` | 纯文本翻译，普通模型即可 |
| 保存密钥设置 | BOOLEAN | √ | 是否自动保存密钥 |
| 目标语言 | 下拉 | `英文` | 英文/中文/日文/韩文/法文/俄文/西班牙文 |
| 源语言 | 下拉 | `自动检测` | 自动检测或指定源语言 |
| 保留标签格式 | BOOLEAN | ✗ | 开启后译文保持逗号分隔的标签列表 |
| 额外要求 | STRING（多行） | 空 | 对翻译的补充说明 |

**输出：**

- `翻译结果` - STRING 类型，可直接连接其他图像/视频生成节点的提示词输入

> **提示**：翻译为纯文本任务，无需视觉模型，`gpt-4o-mini` 即可胜任；开启「保留标签格式」可把中文扩写结果直接转成英文 tag 列表。

---

## 常见问题

### Q1：ComfyUI 启动后看不到「无极 Wuji」分类？

**A：** 请检查 ComfyUI 启动日志中是否出现了 `[ComfyUI-WujiNodes]` 相关输出。如果没有，确认插件文件夹路径正确为 `custom_nodes/ComfyUI-WujiNodes/`，且文件夹名不能包含额外空格。

### Q2：执行 `pip install` 提示「系統找不到指定的路徑」？

**A：** 这是 Python 解释器路径写错了。请按本文「第三步：确认 Python 解释器路径」先用 `dir` 确认 `python_embeded\python.exe` 的真实位置（注意可能是 `python_embeded` 或 `python_embedded`），再用完整路径执行 `pip install`。

### Q3：作词师提示「尚未设置 API 密钥」？

**A：** 你需要先在「无极 API 设置」节点或「无极作词师」节点的 API密钥字段中填入密钥，并将「保存密钥设置」打开后执行一次。

### Q4：可以使用免费/第三方的 API 吗？

**A：** 可以。插件不限制 API 来源，只要兼容 `/chat/completions` 格式即可。将「API网址」修改为对应服务地址即可。

### Q5：图像/视频反推报错「API 调用失败」？

**A：** 多半是「模型名称」用的是不支持视觉的模型（如 `gpt-4o-mini` 部分服务商不支持）。请改用支持视觉的模型（如 `gpt-4o`），并确认 API密钥有效、API网址正确。

### Q6：音乐人生成音频报错？

**A：** 通常是因为 `audiocraft` 未成功安装。在 Windows 上该库需要 MSVC 编译工具，当前版本容错设计不会让 ComfyUI 崩溃，节点执行后会返回静音并在日志输出错误信息。

### Q7：密钥保存在哪里？安全吗？

**A：** 保存在 `ComfyUI-WujiNodes/config.json`。该文件已通过 `.gitignore` 排除，不会被提交到 Git。日志输出时会自动遮蔽密钥内容（如 `sk-1******cdef`）。

---

## 项目结构

```
ComfyUI-WujiNodes/
├── __init__.py              # 插件入口，注册节点
├── config.json              # API 配置（自动生成，不提交 Git）
├── requirements.txt          # Python 依赖列表（audiocraft/transformers 为可选）
├── .gitignore               # Git 忽略规则
├── nodes/
│   ├── __init__.py
│   ├── wuji_settings_node.py   # 无极 API 设置
│   ├── wuji_lyric_node.py      # 无极作词师
│   ├── wuji_music_node.py      # 无极音乐人
│   ├── wuji_image_caption_node.py  # 无极图像反推提示词
│   ├── wuji_video_caption_node.py  # 无极视频反推提示词
│   └── wuji_translate_node.py      # 无极提示词翻译
└── utils/
    ├── __init__.py
    ├── config.py               # 配置读写管理
    ├── llm_api.py              # LLM / 视觉 API 调用
    └── audio_backend.py        # 音乐生成后端
```
