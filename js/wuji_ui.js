// ============================================================
// 无极节点 · ComfyUI 前端 UI 美化脚本 (wuji_ui.js)
// 仅做画布视觉美化：修改节点标题栏颜色、节点底色、输入框/下拉框样式。
// 不调用任何后端 API，不修改翻译、作词等业务逻辑。
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

      // 给节点 DOM 打上标记类，供上面的 CSS 作用（best-effort，失败不影响运行）
      if (this.dom_element) this.dom_element.classList.add("wuji-node");

      return r;
    };
  },
});