// 无极节点 · ComfyUI 前端界面脚本
// ComfyUI 会自动加载 custom_node 的 js/ 目录下的 .js 文件。
// 本脚本负责：注入样式、为各无极节点设定主题配色、在节点上绘制「无极」徽标、补充节点中文说明。
import { app } from "../../scripts/app.js";

// 各无极节点的主题配色与徽标
const NODE_THEME = {
  WujiApiSettings:       { color: "#6a4bbf", bgcolor: "#241a3d", badge: "无极设置" },
  WujiLyricGenerator:    { color: "#9b5bdf", bgcolor: "#2a1a3d", badge: "无极作词" },
  WujiMusician:          { color: "#d98b3d", bgcolor: "#3d2210", badge: "无极音乐" },
  WujiImageCaption:      { color: "#3da8d9", bgcolor: "#0f2430", badge: "图像反推" },
  WujiVideoCaption:      { color: "#3dd9a8", bgcolor: "#0f3024", badge: "视频反推" },
  WujiPromptTranslator:  { color: "#d93d8f", bgcolor: "#301024", badge: "提示词翻译" },
};

app.registerExtension({
  name: "Wuji.Nodes",

  async setup() {
    // 注入同目录下的样式文件
    const sheet = document.createElement("link");
    sheet.rel = "stylesheet";
    sheet.href = new URL("wuji_node_styles.css", import.meta.url).href;
    document.head.appendChild(sheet);
  },

  async beforeRegisterNodeDef(nodeType, nodeData) {
    const theme = NODE_THEME[nodeData.name];
    if (!theme) return;

    // 节点创建时：套用主题配色，并给节点 DOM 加上 wuji-node 类（供 CSS 美化）
    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = onNodeCreated?.apply(this, arguments);
      this.color = theme.color;
      this.bgcolor = theme.bgcolor;
      // best-effort：给节点 DOM 元素加上标记类，CSS 据此美化
      if (this.dom_element) this.dom_element.classList.add("wuji-node");
      return r;
    };

    // 节点绘制时：在左下角绘制「无极」徽标
    const onDrawForeground = nodeType.prototype.onDrawForeground;
    nodeType.prototype.onDrawForeground = function (ctx) {
      const r = onDrawForeground?.apply(this, arguments);
      if (this.flags.collapsed) return r;

      const w = this.size[0];
      const h = this.size[1];
      const label = theme.badge;
      const pad = 6;
      const fontSize = 10;

      ctx.save();
      ctx.font = `${fontSize}px sans-serif`;
      const tw = ctx.measureText(label).width;
      const bw = tw + pad * 2;
      const bx = w - bw - 8;
      const by = h - 22;

      // 徽标底
      ctx.fillStyle = "rgba(255,255,255,0.10)";
      ctx.beginPath();
      if (typeof ctx.roundRect === "function") {
        ctx.roundRect(bx, by, bw, 20, 10);
      } else {
        ctx.rect(bx, by, bw, 20);
      }
      ctx.fill();

      // 徽标文字
      ctx.fillStyle = "rgba(255,255,255,0.85)";
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillText(label, bx + pad, by + 10);
      ctx.restore();

      return r;
    };
  },
});