import { app } from "../../scripts/app.js";

function conditionalWidgetHandler(node) {
  // Handle WanResolutionSelector node
  if (node.comfyClass === "WanResolutionSelector") {
    const modeWidget = findWidgetByName(node, "mode");
    const qualityWidget = findWidgetByName(node, "quality");
    const aroWidget = findWidgetByName(node, "aspect_ratio_override");
    const manualWidthWidget = findWidgetByName(node, "manual_width");
    const manualHeightWidget = findWidgetByName(node, "manual_height");

    // Disable all target widgets by default
    toggleWidget(node, qualityWidget);
    toggleWidget(node, aroWidget);
    toggleWidget(node, manualWidthWidget);
    toggleWidget(node, manualHeightWidget);

    // Enable depending on mode
    const isManual = modeWidget?.value === "manual";
    if (isManual) {
      toggleWidget(node, manualWidthWidget, true);
      toggleWidget(node, manualHeightWidget, true);
    } else {
      // auto mode
      toggleWidget(node, qualityWidget, true);
      toggleWidget(node, aroWidget, true);
    }
  }
  
  // Add other node types here as needed
  // if (node.comfyClass === "AnotherNode") {
  //   // Handle another node type
  // }
}

const findWidgetByName = (node, name) => {
  return node.widgets ? node.widgets.find((w) => w.name === name) : null;
};

function toggleWidget(node, widget, show = false) {
  if (!widget) return;
  widget.disabled = !show;
  node?.setDirtyCanvas?.(true);
}

app.registerExtension({
  name: "J1mB091.ConditionalWidgetVisibility",
  nodeCreated(node) {
    // Only handle nodes that need conditional widget visibility
    const supportedNodes = ["WanResolutionSelector"];
    if (!supportedNodes.includes(node.comfyClass)) return;

    // Initial apply
    conditionalWidgetHandler(node);

    // Re-apply on any widget value change for this node
    for (const w of node.widgets || []) {
      let widgetValue = w.value;

      // Store original descriptor if present
      let originalDescriptor =
        Object.getOwnPropertyDescriptor(w, "value") ||
        Object.getOwnPropertyDescriptor(Object.getPrototypeOf(w), "value") ||
        Object.getOwnPropertyDescriptor(w.constructor.prototype, "value");

      Object.defineProperty(w, "value", {
        get() {
          return originalDescriptor && originalDescriptor.get
            ? originalDescriptor.get.call(w)
            : widgetValue;
        },
        set(newVal) {
          if (originalDescriptor && originalDescriptor.set) {
            originalDescriptor.set.call(w, newVal);
          } else {
            widgetValue = newVal;
          }
          conditionalWidgetHandler(node);
        },
      });
    }
  },
});
