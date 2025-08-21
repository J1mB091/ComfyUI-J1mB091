import { app } from "../../scripts/app.js";

// Constants
const NODE_CLASS_RESOLUTION_SELECTOR = "ResolutionSelector";
const MODE_MANUAL = "manual";
const MODEL_WAN = "WAN";

// Widget names
const WIDGET_NAMES = {
  mode: "mode",
  model: "model",
  quality: "quality",
  aspect_ratio_override: "aspect_ratio_override",
  aspect_ratio: "aspect_ratio",
  manual_width: "manual_width",
  manual_height: "manual_height"
};

function conditionalWidgetHandler(node) {
  // Handle J1mB091's Resolution Selector node
  if (node.comfyClass === NODE_CLASS_RESOLUTION_SELECTOR) {
    const widgets = getResolutionSelectorWidgets(node);

    // Disable all target widgets by default (except mode widget)
    Object.entries(widgets).forEach(([name, widget]) => {
      if (name !== 'mode') {
        toggleWidget(node, widget);
      }
    });

    const isManual = widgets.mode?.value === MODE_MANUAL;
    const isWAN = widgets.model?.value === MODEL_WAN;

    if (isManual) {
      // In manual mode, only show width/height inputs
      toggleWidget(node, widgets.manual_width, true);
      toggleWidget(node, widgets.manual_height, true);
    } else {
      // Auto mode - show model selector and conditional inputs
      toggleWidget(node, widgets.model, true);

      if (isWAN) {
        // WAN: show quality and aspect_ratio_override
        toggleWidget(node, widgets.quality, true);
        toggleWidget(node, widgets.aspect_ratio_override, true);
      } else {
        // FLUX: show aspect_ratio
        toggleWidget(node, widgets.aspect_ratio, true);
      }
    }
  }

  // Add other node types here as needed
}

function getResolutionSelectorWidgets(node) {
  return {
    mode: findWidgetByName(node, WIDGET_NAMES.mode),
    model: findWidgetByName(node, WIDGET_NAMES.model),
    quality: findWidgetByName(node, WIDGET_NAMES.quality),
    aspect_ratio_override: findWidgetByName(node, WIDGET_NAMES.aspect_ratio_override),
    aspect_ratio: findWidgetByName(node, WIDGET_NAMES.aspect_ratio),
    manual_width: findWidgetByName(node, WIDGET_NAMES.manual_width),
    manual_height: findWidgetByName(node, WIDGET_NAMES.manual_height)
  };
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
    const supportedNodes = ["ResolutionSelector"];
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
