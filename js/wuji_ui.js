// ============================================================
// 无极节点 · ComfyUI 前端 UI 美化脚本 (wuji_ui.js)
// 仅做画布视觉美化：修改节点标题栏颜色、节点底色、输入框/下拉框样式。
// 另为「无极图像反推提示词」节点内置图片上传按钮，免除额外拖 LoadImage。
// 兼容新版 ComfyUI：使用官方 registerExtension 接口，代码防御式书写，避免白屏。
// ============================================================
import { app } from "../../scripts/app.js";

// 各无极节点的主题配色（color = 标题栏颜色，bgcolor = 节点底色）
const NODE_THEME = {
  WujiApiSettings:      { color: "#6a4bbf", bgcolor: "#241a3d" }, // 设置 · 紫
  WujiLyricGenerator:   { color: "#9b5bdf", bgcolor: "#2a1a3d" }, // 作词师 · 紫白
  WujiMusician:         { color: "#d98b3d", bgcolor: "#3d2210" }, // 音乐人 · 琥珀
  WujiImageCaption:     { color: "#3da8d9", bgcolor: "#0f2430" }, // 图像反推 · 天蓝
  WujiVideoCaption:     { color: "#3dd9a8", bgcolor: "#0f3024" }, // 视频反推 · 青绿
  WujiPromptTranslator: { color: "#d93d8f", bgcolor: "#301024" }, // 翻译 · 玫红
};

// 内嵌样式：自包含，避免额外网络请求，降低白屏风险
const WUJI_CSS = `
.wuji-node {
  --wuji-accent: #9b5bdf;
}

/* 标题栏文字 */
.wuji-node .title {
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

/* 输入框 / 多行框 / 下拉文本框 */
.wuji-node input,
.wuji-node textarea,
.wuji-node .comfy-multiline-input {
  background: rgba(0, 0, 0, 0.28) !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  border-radius: 6px !important;
  color: #eae6ff !important;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

/* 聚焦高亮 */
.wuji-node input:focus,
.wuji-node textarea:focus,
.wuji-node .comfy-multiline-input:focus {
  border-color: rgba(155, 91, 223, 0.65) !important;
  box-shadow: 0 0 0 2px rgba(155, 91, 223, 0.18);
  outline: none;
}

/* 下拉框按钮 */
.wuji-node .p-combo-widget > .p-combo-widget-label {
  background: rgba(0, 0, 0, 0.28);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  color: #eae6ff;
}

/* 下拉面板 */
.wuji-node .graphdialog {
  background: rgba(30, 22, 46, 0.96) !important;
  border: 1px solid rgba(255, 255, 255, 0.14) !important;
  border-radius: 8px !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35) !important;
}

/* 控件标签 */
.wuji-node .widget-label {
  color: #d9d2ef !important;
  font-size: 12px;
}

/* 选中外框 */
.wuji-node.selected {
  box-shadow: 0 0 0 2px rgba(155, 91, 223, 0.55);
}

/* ---- 图片上传按钮与预览 ---- */
.wuji-image-upload-btn {
  display: inline-block;
  width: 100%;
  padding: 6px 0;
  margin-top: 4px;
  background: rgba(61, 168, 217, 0.18);
  border: 1px dashed rgba(61, 168, 217, 0.45);
  border-radius: 8px;
  color: #3da8d9;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  user-select: none;
}
.wuji-image-upload-btn:hover {
  background: rgba(61, 168, 217, 0.28);
  border-color: #3da8d9;
}

.wuji-image-preview-wrap {
  width: 100%;
  margin-top: 4px;
  border-radius: 6px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.wuji-image-preview-wrap img {
  display: block;
  width: 100%;
  height: auto;
  max-height: 180px;
  object-fit: contain;
}

.wuji-image-clear-btn {
  display: inline-block;
  width: 100%;
  padding: 3px 0;
  margin-top: 2px;
  background: rgba(217, 61, 61, 0.12);
  border: 1px solid rgba(217, 61, 61, 0.3);
  border-radius: 4px;
  color: #d93d3d;
  font-size: 10px;
  text-align: center;
  cursor: pointer;
  transition: background 0.15s;
}
.wuji-image-clear-btn:hover {
  background: rgba(217, 61, 61, 0.2);
}
`;

app.registerExtension({
  name: "Wuji.Nodes.UI",

  async setup() {
    // 注入内嵌样式（自包含，无外部依赖）
    const styleEl = document.createElement("style");
    styleEl.textContent = WUJI_CSS;
    document.head.appendChild(styleEl);
  },

  async beforeRegisterNodeDef(nodeType, nodeData) {
    const theme = NODE_THEME[nodeData.name];
    if (!theme) return;

    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = onNodeCreated?.apply(this, arguments);

      // 修改节点标题栏颜色与节点底色
      this.color = theme.color;
      this.bgcolor = theme.bgcolor;

      // 给节点 DOM 打上标记类，供上面的 CSS 作用
      if (this.dom_element) this.dom_element.classList.add("wuji-node");

      // ======= 为图像反推节点添加内置图片上传按钮 =======
      if (nodeData.name === "WujiImageCaption") {
        _addImageUploadToNode(this);
      }

      return r;
    };
  },
});

// ----------------------------------------------------------
// 图片上传功能（仅为无极图像反推节点服务）
// ----------------------------------------------------------

/**
 * 在图像反推节点上添加上传按钮、预览图和清除按钮。
 * 隐藏后端「图片文件」STRING widget 的文本框，用上传按钮替代。
 */
function _addImageUploadToNode(node) {
  // 找到「图片文件」widget（optional 中的 STRING widget）
  const fileWidget = node.widgets?.find(w => w.name === "图片文件");
  if (!fileWidget) return;

  // 隐藏其默认文本框
  fileWidget.type = "hidden";
  if (fileWidget.inputEl) fileWidget.inputEl.style.display = "none";

  // 创建上传按钮 DOM
  const btn = document.createElement("div");
  btn.className = "wuji-image-upload-btn";
  btn.textContent = "选择图片";

  // 创建预览容器
  const previewWrap = document.createElement("div");
  previewWrap.className = "wuji-image-preview-wrap";
  previewWrap.style.display = "none";

  const previewImg = document.createElement("img");
  previewWrap.appendChild(previewImg);

  // 创建清除按钮
  const clearBtn = document.createElement("div");
  clearBtn.className = "wuji-image-clear-btn";
  clearBtn.textContent = "清除图片";
  clearBtn.style.display = "none";

  // 插入节点 DOM：在文件 widget 所在行之后展示
  node.addDOMWidget("图片上传", "custom", {
    callback: () => {
      // 将我们的 DOM 元素插到 node 内容区中
      _injectDomElements(node, fileWidget, btn, previewWrap, clearBtn);
      _bindImageUpload(node, fileWidget, btn, previewImg, previewWrap, clearBtn, "选择图片");
    },
  });
}

function _injectDomElements(node, fileWidget, btn, previewWrap, clearBtn) {
  // 在文件 widget 下方插入我们的 UI
  const refEl = fileWidget.element?.parentElement || fileWidget.inputEl?.parentElement;
  if (!refEl) return;

  if (refEl.nextSibling !== btn) {
    refEl.after(clearBtn, previewWrap, btn);
  }
}

function _bindImageUpload(node, fileWidget, uploadBtn, previewImg, previewWrap, clearBtn, originalText) {
  // 如果已有值，恢复预览
  if (fileWidget.value) {
    _showPreview(fileWidget.value, previewImg, previewWrap, clearBtn);
    uploadBtn.textContent = "更换图片";
  }

  // 上传按钮点击：创建隐藏 file input 触发文件选择
  uploadBtn.onclick = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/png,image/jpeg,image/webp,image/gif,image/bmp";
    input.style.display = "none";

    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file) return;

      try {
        const formData = new FormData();
        formData.append("image", file);

        // 调用 ComfyUI 的上传接口
        const resp = await fetch("/upload/image", {
          method: "POST",
          body: formData,
        });

        if (!resp.ok) {
          const txt = await resp.text();
          throw new Error(`上传失败 (${resp.status}): ${txt}`);
        }

        const data = await resp.json();
        const uploadedName = data.name || data.filename || file.name;
        // 取相对 input 目录名（有些版本返回 "input/xxx.png"，有些返回 "xxx.png"）
        const shortName = uploadedName.replace(/^(input[\\/])+/i, "");

        // 写入 widget 值
        fileWidget.value = shortName;
        _showPreview(shortName, previewImg, previewWrap, clearBtn);
        uploadBtn.textContent = "更换图片";

        // 标记节点需要重新执行，触发 graph 重绘
        node.setDirtyCanvas(true, true);
        if (node.onWidgetChanged) node.onWidgetChanged("图片文件", shortName, "", shortName);

        console.log("[WujiNodes] 图片已上传 →", shortName);
      } catch (err) {
        console.error("[WujiNodes] 图片上传失败：", err);
        alert("图片上传失败：" + err.message);
      }
    };

    document.body.appendChild(input);
    input.click();
    setTimeout(() => input.remove(), 60000);
  };

  // 清除按钮
  clearBtn.onclick = () => {
    fileWidget.value = "";
    previewImg.src = "";
    previewWrap.style.display = "none";
    clearBtn.style.display = "none";
    uploadBtn.textContent = originalText || "选择图片";
    node.setDirtyCanvas(true, true);
  };
}

function _showPreview(filename, previewImg, previewWrap, clearBtn) {
  if (!filename) {
    previewImg.src = "";
    previewWrap.style.display = "none";
    clearBtn.style.display = "none";
    return;
  }

  // ComfyUI 的 /view?filename=... 接口
  const url = "/view?filename=" + encodeURIComponent(filename) + "&type=input";
  previewImg.src = url;
  previewImg.onerror = () => {
    // 如果 /view 不可用，尝试直接引用 input 目录
    previewImg.src = "input/" + encodeURIComponent(filename);
  };
  previewWrap.style.display = "block";
  clearBtn.style.display = "block";
}
