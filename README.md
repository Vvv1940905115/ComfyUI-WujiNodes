# 工坊提示词

一站式 ComfyUI 提示词工具套件：图片视频反推提示词、全局输入框一键翻译、提示词优化、AI 歌词与音乐生成。

![节点数](https://img.shields.io/badge/节点-5个-purple)
![许可证](https://img.shields.io/badge/license-MIT-green)

---

## 目录

- [功能简介](#功能简介)
- [环境要求](#环境要求)
- [安装教程（超详细步骤）](#安装教程超详细步骤)
  - [第一步：确认 ComfyUI 已安装](#第一步确认-comfyui-已安装)
  - [第二步：获取插件文件到 custom_nodes](#第二步获取插件文件到-custom_nodes)
  - [第三步：定位 Python 解释器（最容易出错的一步）](#第三步定位-python-解释器最容易出错的一步)
  - [第四步：安装 Python 依赖包](#第四步安装-python-依赖包)
  - [第五步：重启 ComfyUI 并验证](#第五步重启-comfyui-并验证)
  - [如何更新插件](#如何更新插件)
  - [补充：依赖未安装 / 缺失时的处理](#补充依赖未安装--缺失时的处理)
  - [Windows 下安装 audiocraft 的特别说明（可选）](#windows-下安装-audiocraft-的特别说明可选)
- [配置 API 密钥（第一次使用必读）](#配置-api-密钥第一次使用必读)
  - [在哪填写密钥？](#在哪填写密钥)
  - [密钥会保存到哪里？](#密钥会保存到哪里)
  - [支持哪些 API 服务商？](#支持哪些-api-服务商)
  - [首次快速上手流程](#首次快速上手流程)
- [节点详细说明](#节点详细说明)
  - [工坊作词师](#工坊作词师)
  - [工坊音乐人](#工坊音乐人)
  - [工坊图像反推提示词](#工坊图像反推提示词)
  - [工坊视频反推提示词](#工坊视频反推提示词)
  - [工坊提示词翻译](#工坊提示词翻译)
- [提示词优化与翻译工具栏](#提示词优化与翻译工具栏)
- [常见问题（FAQ）](#常见问题faq)
- [项目文件结构](#项目文件结构)

---

## 功能简介

| 节点 | 功能 | 核心依赖 |
|------|------|----------|
| 工坊作词师 | 调用 LLM 生成结构化歌词（Verse/Chorus/Bridge/Outro） | `openai` 或 `requests` |
| 工坊音乐人 | 根据歌词 + 文本描述生成音频 | `audiocraft`（可选，缺失时返回静音） |
| 工坊图像反推提示词 | 调用视觉模型反推图片的生成提示词 | `openai` 或 `requests` |
| 工坊视频反推提示词 | 抽帧后调用视觉模型反推视频的生成提示词 | `openai` 或 `requests` + `ffmpeg` |
| 工坊提示词翻译 | 将提示词在多种语言间互译，便于跨模型使用 | `openai` 或 `requests` |

> **附加能力（非节点）**：插件还会在所有文本输入框右侧自动注入一组「提示词优化 / 翻译」悬浮按钮，支持快捷键 `Ctrl+Shift+O`（优化）与 `Ctrl+Shift+T`（翻译）。详见下方「提示词优化 / 翻译工具栏」。

> **关于「工坊音乐人」**：该节点依赖 Meta 的 `audiocraft` 库，在 Windows 便携版 Python 上安装较复杂。即使未装，也不会导致 ComfyUI 崩溃——执行时会安全返回静音并输出错误日志。详见下方安装说明。

---

## 环境要求

- **ComfyUI** 已安装并能正常启动、打开 Web 界面
- **Python 3.10+**（ComfyUI 自带的嵌入式 Python 通常满足）
- **OpenAI 兼容 API**：需要一个可用的 `/chat/completions` 格式的 API（OpenAI 官方 / DeepSeek / Groq / 国内中转代理均可）

---

## 安装教程（超详细步骤）

> 以下每一步都可独立执行。如果某一步你已确认完成，可直接跳到下一步。

### 第一步：确认 ComfyUI 已安装

先确认 ComfyUI 能正常启动、浏览器能打开 `http://127.0.0.1:8188`。如果还没装 ComfyUI，先去装好再回来。

**记下你的 ComfyUI 根目录**，后面会反复用到。常见位置例如：

```
D:\Ai\ComfyUI\ComfyUI\
```

插件的最终路径必须是：

```
ComfyUI\
└── custom_nodes\
    └── ComfyUI-PromptWorkshop\   ← 插件放这里，文件夹名不能改
```

---

### 第二步：获取插件文件到 custom_nodes

#### 方式 A：Git 克隆（推荐，方便后续 `git pull` 更新）

1. 打开 **PowerShell**（不是 CMD），进入 ComfyUI 的 `custom_nodes` 目录：

   ```powershell
   cd D:\Ai\ComfyUI\ComfyUI\custom_nodes
   ```

   > 请把路径换成你自己的 ComfyUI 根目录。

2. 克隆本仓库：

   ```powershell
   git clone https://github.com/Vvv1940905115/ComfyUI-PromptWorkshop.git
   ```

3. 检查是否克隆成功：

   ```powershell
   dir ComfyUI-PromptWorkshop
   ```

   应该能看到 `__init__.py`、`nodes\`、`utils\`、`js\`、`requirements.txt` 等文件。

#### 方式 B：手动下载 ZIP（没有 git 时使用）

1. 浏览器打开 [GitHub 仓库页面](https://github.com/Vvv1940905115/ComfyUI-PromptWorkshop)
2. 点击绿色按钮 **`<> Code`** → **`Download ZIP`**
3. 将下载的 `ComfyUI-PromptWorkshop-main.zip` 解压
4. 将解压出的 `ComfyUI-PromptWorkshop-main` 文件夹**重命名为** `ComfyUI-PromptWorkshop`（去掉 `-main` 后缀）
5. 把整个 `ComfyUI-PromptWorkshop` 文件夹复制到 `ComfyUI\custom_nodes\` 下

   > **文件夹名必须是 `ComfyUI-PromptWorkshop`**，不能包含额外空格或后缀，否则 ComfyUI 无法识别。

#### 方式 C：通过 ComfyUI Manager 安装（最简单）

如果你的 ComfyUI 已安装了 [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager)：

1. 打开 ComfyUI → 点击右上角 **Manager** 按钮
2. 选择 **`Install via Git URL`**
3. 粘贴本仓库地址：`https://github.com/Vvv1940905115/ComfyUI-PromptWorkshop.git`
4. 点击确认，等待克隆完成
5. **重启 ComfyUI** 即可生效

> ComfyUI Manager 会自动完成依赖安装，无需手动执行 `pip install`。如果安装后仍有缺失依赖报错，请参考下方的补充处理步骤。

---

### 第三步：定位 Python 解释器（最容易出错的一步）

> 这是安装过程中**最容易踩坑**的地方。依赖必须装进「运行 ComfyUI 的那个 Python」里，装错了等于没装。

#### 情况 1：便携版 ComfyUI（有 `python_embeded` 文件夹）

大多数 Windows 用户用的是便携版。进入 ComfyUI 根目录，找 `python_embeded`（也可能叫 `python_embedded`，多一个字母 `d`）：

```powershell
# 先确认 python.exe 存在
dir D:\Ai\ComfyUI\ComfyUI\python_embeded\python.exe
```

如果上面报「找不到路径」，逐个试：

```powershell
dir D:\Ai\ComfyUI\ComfyUI\python_embeded\
dir D:\Ai\ComfyUI\ComfyUI\python_embedded\
```

找到后，你的 Python 路径就是类似：

```
D:\Ai\ComfyUI\ComfyUI\python_embeded\python.exe
```

#### 情况 2：系统 Python / venv 环境安装的 ComfyUI

直接用系统 Python：

```powershell
where python
python --version
```

确保版本 ≥ 3.10。

#### 把路径记下来

后面的安装命令里，便携版用**完整路径**调用，系统 Python 用 `python` / `pip` 直接调用：

| ComfyUI 类型 | 调用方式（示例） |
|-------------|-----------------|
| 便携版 | `D:\Ai\ComfyUI\ComfyUI\python_embeded\python.exe -m pip install ...` |
| 系统/venv | `pip install ...` |

---

### 第四步：安装 Python 依赖包

先在 PowerShell 中进入插件目录：

```powershell
cd D:\Ai\ComfyUI\ComfyUI\custom_nodes\ComfyUI-PromptWorkshop
```

然后根据你的 ComfyUI 类型执行对应命令：

#### 便携版 ComfyUI（使用完整 Python 路径）

```powershell
D:\Ai\ComfyUI\ComfyUI\python_embeded\python.exe -m pip install -r requirements.txt
```

> **常见问题 1**：如果提示 `No module named pip`，需要先安装 pip：
> ```powershell
> D:\Ai\ComfyUI\ComfyUI\python_embeded\python.exe -m ensurepip
> ```
>
> **常见问题 2**：如果提示 `externally-managed-environment` 错误（便携版新版 Python），临时加 `--break-system-packages` 即可：
> ```powershell
> D:\Ai\ComfyUI\ComfyUI\python_embeded\python.exe -m pip install --break-system-packages -r requirements.txt
> ```
>
> **常见问题 3**：如果提示找不到 `python_embeded` 目录，某些 ComfyUI 版本将其命名为 `python_embedded`（多一个字母 d）。用 `dir` 命令逐个确认：
> ```powershell
> dir D:\Ai\ComfyUI\ComfyUI\python_embeded\   # 常见写法
> dir D:\Ai\ComfyUI\ComfyUI\python_embedded\  # 备选写法
> ```

#### 系统 / venv Python 安装的 ComfyUI

```powershell
pip install -r requirements.txt
```

#### 安装成功标志

你会看到类似这样的输出：

```
Successfully installed numpy-xxx Pillow-xxx openai-xxx ...
```

> `requirements.txt` 默认只包含必需依赖（`torch` / `torchaudio` / `numpy` / `Pillow` / `openai` / `requests`）。
> `audiocraft` 和 `transformers` 是**可选依赖**，默认不会安装，避免 Windows 下编译失败卡住。
>
> **关于 `torch` / `torchaudio`**：这两个包通常已随 ComfyUI 自带，`pip install` 会检测到已安装版本并跳过，一般不会导致版本冲突。如果遇到 torch 版本问题，可临时移除 `requirements.txt` 中前两行后重试。

---

### 第五步：重启 ComfyUI 并验证

1. **完全关闭 ComfyUI**（关闭终端窗口，不是只刷新网页）
2. 重新启动 ComfyUI（双击 `run_nvidia_gpu.bat` 或你的启动脚本）
3. 观察启动日志（黑色终端窗口），应该能看到紫色高亮的一行：

   ```
   [ComfyUI-PromptWorkshop] 已载入 5 个节点：
   工坊作词师、工坊音乐人、工坊图像反推提示词、工坊视频反推提示词、工坊提示词翻译 | API密钥=(未设置)
   ```

4. 打开浏览器进入 ComfyUI Web 界面，在空白处右键 → **`Add Node`**，在节点菜单里找到 **`工坊提示词`** 分类，下面应有 3 个子分类：
   - `工坊提示词/作词` → 工坊作词师
   - `工坊提示词/音乐` → 工坊音乐人
   - `工坊提示词/反推` → 工坊图像反推提示词、工坊视频反推提示词、工坊提示词翻译

   全部 5 个节点可见 = 安装成功。

---

### 如何更新插件

如果以后有新版本推送，你可以这样更新：

**用 Git 克隆的用户：**

```powershell
cd D:\Ai\ComfyUI\ComfyUI\custom_nodes\ComfyUI-PromptWorkshop
git pull
```

然后**重启 ComfyUI** 即可。一般无需重新 pip install，除非 `requirements.txt` 有新增依赖。

**手动下载 ZIP 的用户：**

重复「第二步 - 方式 B」的流程：下载最新 ZIP → 解压 → 覆盖原有 `ComfyUI-PromptWorkshop` 文件夹 → 重启 ComfyUI。

---

## 补充：依赖未安装 / 缺失时的处理

如果启动后报错缺少某个包，或某些节点执行时报错，请按以下步骤补装。

#### 1. 一键补装全部依赖

```powershell
# 先进入插件目录
cd D:\Ai\ComfyUI\ComfyUI\custom_nodes\ComfyUI-PromptWorkshop

# 便携版
D:\Ai\ComfyUI\ComfyUI\python_embeded\python.exe -m pip install -r requirements.txt

# 系统 Python
pip install -r requirements.txt
```

#### 2. 只安装缺失的单个包

```powershell
# 便携版（以 Pillow 为例）
D:\Ai\ComfyUI\ComfyUI\python_embeded\python.exe -m pip install Pillow

# 系统 Python
pip install Pillow
```

#### 3. 各依赖包的用途与缺失表现

| 包名 | 用途 | 缺失时的表现 |
|------|------|-------------|
| `torch` / `torchaudio` | ComfyUI 基础运行 | ComfyUI 本身无法运行（通常已自带） |
| `Pillow` | 图像编解码（反推节点需要） | 反推节点报「图像编码失败」 |
| `openai` | 调用 LLM / 视觉模型（优先方案） | 自动降级到 `requests`，一般不影响 |
| `requests` | 调用 LLM / 视觉模型（降级方案） | `openai` 和 `requests` 都没有时 API 调用失败 |
| `audiocraft` | 「工坊音乐人」生成音频 | 该节点安全返回静音，不崩溃（详见下方说明） |
| `transformers` | 部分后端可选依赖 | 非必需 |

#### 4. 装完别忘了重启

```powershell
# 装完后重启 ComfyUI 使新装的包生效
```

---

### Windows 下安装 audiocraft 的特别说明（可选）

如果你想让「工坊音乐人」真正出声，需要额外安装 `audiocraft`。这个库在 Windows 上需要 MSVC 编译工具，且在 Python 3.13 下极易编译失败。

**推荐做法：**

1. 使用 **Python 3.10 或 3.11** 的 ComfyUI 便携版环境
2. 安装 [Microsoft C++ 生成工具](https://visualstudio.microsoft.com/zh-hans/visual-cpp-build-tools/)（安装时勾选「C++ 桌面开发」工作负载）
3. 在该 Python 下执行：

   ```powershell
   D:\Ai\ComfyUI\ComfyUI\python_embeded\python.exe -m pip install audiocraft
   ```

即使不装，`工坊音乐人` 节点也不会导致 ComfyUI 崩溃，只返回静音与错误日志。

---

## 配置 API 密钥（第一次使用必读）

本插件的所有 AI 功能（作词、音乐、反推、翻译）都需要 OpenAI 兼容 API。每个需要 API 的节点都自带 API 配置字段，填写一次即可自动保存复用。

### 在哪填写密钥？

在以下任意一个节点的参数面板中：

- **工坊作词师**
- **工坊图像反推提示词**
- **工坊视频反推提示词**
- **工坊提示词翻译**

你会看到三个共用字段：

| 字段 | 说明 | 默认值 |
|------|------|--------|
| **API密钥** | 你的 OpenAI 格式 API Key（如 `sk-...`） | 空 |
| **API网址** | API 请求的基础地址 | `https://api.openai.com/v1` |
| **模型名称** | 使用的模型 ID | `gpt-4o-mini` |
| **保存密钥设置** | 开启（✅）时自动保存到本地 | 默认开启 |

> **操作方式**：在任意一个节点的以上字段填好 → 确保「保存密钥设置」为 ✅ → 按 **Ctrl+Enter** 执行一次。密钥即自动保存并供所有其他节点共享。

### 密钥会保存到哪里？

保存在插件目录下的 `config.json` 文件中（仅本地存储），内容格式如下：

```json
{
  "api_key": "sk-xxxxxxxxxxxxxxxx",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4o-mini"
}
```

- **安全**：该文件已通过 `.gitignore` 排除，不会被提交到 GitHub
- **遮蔽**：ComfyUI 日志输出时会自动遮蔽密钥，显示如 `sk-1******cdef`
- **只写一次**：在一个节点填好并执行后，其他节点打开时会自动读取已保存的值
- **文件权限**：保存时自动设为 `600`（仅当前用户可读写，Windows 上可能忽略）
- **生命周期**：首次执行任意带 API 字段的节点时自动生成 → 每次修改保存密钥设置并执行时更新 → 删除文件可重置为默认配置

### 支持哪些 API 服务商？

插件不限制 API 来源，只要兼容 OpenAI `POST /chat/completions` 格式即可：

| 服务商 | API网址 | 模型名称示例 | 备注 |
|--------|---------|-------------|------|
| OpenAI 官方 | `https://api.openai.com/v1` | `gpt-4o-mini` | 付费 |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` | 低价 |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b` | 免费额度 |
| 国内中转代理 | 填入代理提供的地址 | 按代理说明 | 方便国内访问 |
| Ollama 本地 | `http://localhost:11434/v1` | `llama3.2-vision` | 需安装 Ollama |

> **重要提醒**：图像反推、视频反推功能需要**支持视觉的模型**。`gpt-4o-mini` 在部分服务商（如 DeepSeek）不支持视觉输入，会导致调用失败。请确保模型名称对应的是多模态模型（如 `gpt-4o`、`llama3.2-vision` 等）。

### 首次快速上手流程

装好插件、配好密钥后，最快的体验路径：

1. **配密钥**：拖入「工坊作词师」节点 → 填 API密钥 / API网址 / 模型名称 → 确保保存密钥设置 ✅ → 执行（Ctrl+Enter）。此后其他节点自动共享，无需重复填写。
2. **试作词**：在同一个「工坊作词师」节点中填写「主题动力源」（如"夏天的海边"）→ 执行 → 右侧 `生成歌词` 输出即出完整歌词。
3. **试图像反推**：拖入「工坊图像反推提示词」→ 连接一张图片（Load Image 节点）→ 选「扩写模式」为"通用"→ 执行 → 得到反推提示词。
4. **试翻译**：把上一步的提示词连入「工坊提示词翻译」→ 目标语言选"英文"→ 执行 → 得到英文 tag。
5. **试工具栏**：在任意文本输入框输入提示词 → 点击输入框右侧的「优化」按钮或按 `Ctrl+Shift+O` → 内容被自动润色；按 `Ctrl+Shift+T` 可中英互译。

---

## 节点详细说明

### 工坊作词师

调用 LLM 生成包含 Verse / Chorus / Bridge / Outro 结构的完整歌词。

**必填参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| API密钥 | STRING | 自动读取 | 首次需要手动填入，保存后自动复用 |
| API网址 | STRING | `https://api.openai.com/v1` | 兼容 OpenAI 格式的 API 地址 |
| 模型名称 | STRING | `gpt-4o-mini` | 纯文本生成，普通模型即可 |
| 保存密钥设置 | BOOLEAN | ✅ | 打开时自动保存密钥到 config.json |
| 主题动力源 | STRING（多行） | `一位在城市打拼的上班族` | 歌曲主题描述，越具体越好 |
| 成品歌词参考 | STRING（多行） | 空 | 可选，贴上参考歌词以模仿其风格 |
| 手动标签 | STRING | `孤独, 奋斗, 希望` | 中文关键词 |
| 英文标签 | STRING | `city, night, dream` | 英文关键词 |
| 性别声色 | 下拉 | `中性` | 女性 / 男性 / 中性 |
| 押韵方案 | 下拉 | `自由` | AABB / ABAB / AAAA / 自由 |
| 语言选择 | 下拉 | `中文` | 中文 / 英文 / 中英混合 |

**可选参数：**

| 参数 | 类型 | 默认值 |
|------|------|--------|
| 进阶_流派 | STRING | `流行摇滚` |
| 进阶_情绪 | STRING | `略带沧桑却充满力量` |
| 进阶_乐器 | STRING | `钢琴, 电吉他, 贝斯` |
| 进阶_BPM | INT | `120`（范围 40-200） |
| 进阶_拍号 | 下拉 | `4/4`（4/4 / 3/4 / 6/8） |
| 进阶_调式 | 下拉 | `C大调`（C大调 / A小调 / G大调） |
| 标签数量 | INT | `3`（范围 1-10） |

**输出：** `生成歌词`（STRING）

---

### 工坊音乐人

接收歌词文本和音频描述，调用 MusicGen 模型生成音频。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| 歌词输入 | STRING（强制输入） | - | 连接作词师的输出 |
| 音频描述 | STRING | `piano, soft, melody` | 风格提示词（英文更佳） |
| cfg_scale | FLOAT | `2.0`（0-10） | CFG 引导强度，越大越贴近描述 |
| 采样步数 | INT | `20`（1-150） | 采样步数，步数越多质量越高但更慢 |
| 种子 | INT | 随机 | 随机种子，固定种子可复现结果 |
| control_after_generate | 下拉 | `randomize` | 种子行为：randomize / fixed / increment / decrement |
| 预估时长_秒 | INT（可选） | `30`（5-300） | 生成音频的目标时长 |

**输出：**
- `音频波形`（AUDIO）— 可连接音频播放节点
- `信息日志`（STRING）— 生成详情、形状、采样率

> **关于模型**：当前使用 Meta `facebook/musicgen-melody` 模型。需要先安装 `audiocraft` 库（可选，见安装教程中的特别说明），未安装时节点安全返回静音。

---

### 工坊图像反推提示词

调用支持视觉的模型（如 GPT-4o、Gemini 等多模态模型），根据输入图片反推其生成提示词。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| 图像 | IMAGE（强制输入） | - | 连接 Load Image 等节点输出的图片 |
| API密钥 | STRING | 自动读取 | 首次需要手动填入，保存后自动复用 |
| API网址 | STRING | `https://api.openai.com/v1` | |
| 模型名称 | STRING | `gpt-4o-mini` | ⚠️ 必须使用支持视觉的模型 |
| 保存密钥设置 | BOOLEAN | ✅ | |
| 扩写模式 | 下拉 | `通用` | 见下方说明 |
| 提示词风格 | 下拉 | `详细描述` | 详细描述 / 简短标签 / 英文提示词 / 中英混合 |
| 额外要求 | STRING（多行） | 空 | 对反推结果的补充说明 |

**输出：** `反推提示词`（STRING）

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

> ⚠️ **必须用视觉模型**：反推功能依赖视觉模型。请在「模型名称」填入支持图像输入的模型（如 `gpt-4o`）。默认的 `gpt-4o-mini` 在部分服务商不支持视觉。

---

### 工坊视频反推提示词

输入视频文件或视频帧序列，均匀抽帧后一并发送给视觉模型，反推视频生成提示词。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| 图像（可选） | IMAGE | - | 可连接 Load Image 添加参考图 |
| 视频（可选） | VHS / IMAGE | - | 连接视频节点（支持 VHS_VIDEOFORMAT 或 IMAGE 序列） |
| API密钥 | STRING | 自动读取 | 首次需要手动填入，保存后自动复用 |
| API网址 | STRING | `https://api.openai.com/v1` | |
| 模型名称 | STRING | `gpt-4o-mini` | ⚠️ 必须使用支持视觉的模型 |
| 保存密钥设置 | BOOLEAN | ✅ | |
| 反推模式 | 下拉 | `复刻` | 复刻 / 重构 / 分镜解构 |
| 抽取帧数 | INT | `8`（1-32） | 从视频中抽取的帧数上限 |
| 提示词风格 | 下拉 | `详细描述` | 详细描述 / 简短标签 / 英文提示词 / 中英混合 |
| 额外要求 | STRING（多行） | 空 | 对反推结果的补充说明 |

**输出：** `反推提示词`（STRING）

**反推模式说明：**

| 模式 | 行为 |
|------|------|
| 复刻 | 精确还原原视频，输出可用于 1:1 复刻的生成提示词 |
| 重构 | 保留原视频风格与情绪，重新设计镜头与叙事 |
| 分镜解构 | 逐镜拆解视频，按帧序输出每镜的画面描述、镜头运动与可复用分镜提示词 |

> ⚠️ **必须用视觉模型**，同上。对于视频文件格式（如 `.mp4`），需要你的系统上有可用的 `ffmpeg` 来抽帧。

---

### 工坊提示词翻译

将已有提示词在多种语言之间互译，便于跨模型复用。例如把中文扩写结果译为英文 tags 供 Stable Diffusion 使用。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| 提示词 | STRING（强制输入） | - | 连接上游反推 / 作词节点的输出 |
| API密钥 | STRING | 自动读取 | 首次需要手动填入，保存后自动复用 |
| API网址 | STRING | `https://api.openai.com/v1` | |
| 模型名称 | STRING | `gpt-4o-mini` | 纯文本翻译，普通模型即可 |
| 保存密钥设置 | BOOLEAN | ✅ | |
| 目标语言 | 下拉 | `英文` | 英文/中文/日文/韩文/法文/俄文/西班牙文 |
| 源语言 | 下拉 | `自动检测` | 自动检测或手动指定源语言 |
| 保留标签格式 | BOOLEAN | ❌ | 开启后译文保持逗号分隔的标签列表格式 |
| 额外要求 | STRING（多行） | 空 | 对翻译结果的补充说明 |

**输出：** `翻译结果`（STRING）

> **纯文本任务**，无需视觉模型，`gpt-4o-mini` 即可胜任。开启「保留标签格式」可把中文扩写结果直接转成英文 tag 列表。

---

## 提示词优化与翻译工具栏

除了上面的独立节点，插件还会在**所有文本输入框**右侧自动注入一组一体化悬浮按钮组：

| 按钮 | 图标 | 功能 | 快捷键 |
|------|------|------|--------|
| 提示词优化 | 铅笔 | 调用 LLM 对输入框内的提示词进行专业润色优化，让细节更丰富、更符合模型习惯 | `Ctrl + Shift + O` |
| 翻译 | 语言 | 自动识别中英文互译：中文 → 英文标签列表、英文 → 流畅中文 | `Ctrl + Shift + T` |

**使用方式：**

1. 把光标放进任意文本输入框（作词、反推、翻译，甚至第三方节点的文本输入框均可）。
2. 点击输入框右侧悬浮的按钮，或直接按对应快捷键。
3. 结果会直接替换当前输入框的内容。

> **说明**：工具栏调用 `POST /wuji/optimize_prompt` 与 `POST /wuji/translate` 两个后端接口，同样复用 `config.json` 中保存的 API 配置，无需单独配置密钥。

---

## 常见问题（FAQ）

### Q1：ComfyUI 启动后看不到「工坊提示词」分类？

**A：** 请检查 ComfyUI 启动日志中是否出现了紫色的 `[ComfyUI-PromptWorkshop]` 输出。

- 如果没有：确认文件夹路径正确为 `custom_nodes/ComfyUI-PromptWorkshop/`
- 注意文件夹名不能包含额外空格，如 `ComfyUI-PromptWorkshop (1)` 或 `ComfyUI-PromptWorkshop-main` 都不能被识别
- 下载 ZIP 解压的用户，务必把 `ComfyUI-PromptWorkshop-main` 重命名为 `ComfyUI-PromptWorkshop`

### Q2：执行 `pip install` 提示「系统找不到指定的路径」？

**A：** 这是 Python 解释器路径写错了。请回到「第三步」仔细确认 `python_embeded\python.exe` 的真实位置——注意有些版本叫 `python_embeded`，有些叫 `python_embedded`（多一个字母 `d`）。用 `dir` 命令逐个检查确认。

### Q3：执行节点提示「尚未设置 API 密钥」？

**A：** 首次使用需要在任意一个需要 API 的节点（如工坊作词师）中：
1. 填写 API密钥 + API网址 + 模型名称
2. 确保「保存密钥设置」为 ✅
3. 按 Ctrl+Enter 执行一次

之后所有节点都会自动读取保存的密钥。

### Q4：可以使用免费 / 第三方的 API 吗？

**A：** 完全可以。插件不限制 API 来源，只要兼容 `POST /chat/completions` 格式即可。修改「API网址」为对应服务地址即可。DeepSeek、Groq 等都兼容，Groq 还有免费额度。

### Q5：图像 / 视频反推报错「API 调用失败」？

**A：** 几乎可以肯定是「模型名称」填的是不支持视觉的模型。比如：
- `gpt-4o-mini` 在 DeepSeek 不支持视觉 → 换成 `gpt-4o`
- 用了纯文本模型 → 换成多模态模型

同时确认 API 密钥有效、API 网址正确。

### Q6：音乐人生成音频报错 / 没声音？

**A：** 通常是因为 `audiocraft` 未安装（它是可选依赖）。在当前版本设计下，该节点缺失 audiocraft 时不会导致 ComfyUI 崩溃，会安全返回静音。如果需要真正生成音乐，请参考安装教程中的「Windows 下安装 audiocraft 的特别说明」。

### Q7：密钥保存在哪里？安全吗？

**A：** 保存在 `ComfyUI-PromptWorkshop/config.json`。

- 该文件已通过 `.gitignore` 排除，不会被 Git 提交
- 日志输出时密钥会自动遮蔽（如 `sk-1******cdef`）
- 仅存储在你自己电脑本地

---

## 项目文件结构

```
ComfyUI-PromptWorkshop/
├── __init__.py                        # 插件入口，注册全部节点
├── server.py                          # 工具栏后端 API 路由（提示词优化 / 翻译）
├── config.json                        # API 配置（自动生成，不提交 Git）
├── requirements.txt                   # Python 依赖列表
├── .gitignore                         # Git 忽略规则
├── README.md                          # 本文档
├── js/
│   ├── wuji_ui.js                     # 前端扩展：注入提示词优化 / 翻译悬浮按钮
│   └── wuji_styles.css                # 悬浮按钮组样式
├── nodes/
│   ├── __init__.py
│   ├── wuji_lyric_node.py             # 工坊作词师
│   ├── wuji_music_node.py             # 工坊音乐人
│   ├── wuji_image_caption_node.py     # 工坊图像反推提示词
│   ├── wuji_video_caption_node.py     # 工坊视频反推提示词
│   └── wuji_translate_node.py         # 工坊提示词翻译
└── utils/
    ├── __init__.py
    ├── config.py                      # 配置读写管理（config.json）
    ├── llm_api.py                     # LLM / 视觉 API 调用核心（含优化 / 翻译）
    └── audio_backend.py               # 音乐生成后端（MusicGen）
```
