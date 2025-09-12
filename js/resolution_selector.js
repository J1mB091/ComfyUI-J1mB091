import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "J1mB091.ResolutionSelector",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "ResolutionSelector") {
            // Store resolution presets for each model
            const MODEL_PRESETS = {
                "FLUX": [
                    "640×1504  (9:21)",
                    "688×1456  (9:19)",
                    "704×1248  (9:16)",
                    "768×1232  (5:8)",
                    "800×1120  (5:7)",
                    "832×1040  (4:5)",
                    "880×1168  (3:4)",
                    "896×1120  (4:5)",
                    "944×1184  (2:3)",
                    "960×1280  (3:5)",
                    "1024×1024  (1:1)",
                    "1120×896  (5:4)",
                    "1184×944  (5:4)",
                    "1216×912  (4:3)",
                    "1248×832  (3:2)",
                    "1280×768  (5:3)",
                    "1344×768  (7:5)",
                    "1360×848  (8:5)",
                    "1408×792  (16:9)",
                    "1472×768  (19:9)",
                    "1504×640  (21:9)",
                    "1536×432  (32:9)"
                ],
                "FLUX Kontext": [
                    "672×1568  (9:21)",
                    "688×1504  (9:19.5)",
                    "720×1456  (9:18)",
                    "752×1392  (9:17)",
                    "800×1328  (5:8)",
                    "832×1248  (2:3)",
                    "880×1184  (3:4)",
                    "944×1104  (4:5)",
                    "1024×1024  (1:1)",
                    "1104×944  (5:4)",
                    "1184×880  (4:3)",
                    "1248×832  (3:2)",
                    "1328×800  (8:5)",
                    "1392×752  (17:9)",
                    "1456×720  (18:9)",
                    "1504×688  (19.5:9)",
                    "1568×672  (21:9)"
                ],
                "SDXL": [
                    "640×1536  (5:12)",
                    "768×1344  (4:7)",
                    "832×1216  (2:3)",
                    "896×1152  (7:9)",
                    "1024×1024  (1:1)",
                    "1152×896  (9:7)",
                    "1216×832  (3:2)",
                    "1344×768  (7:4)",
                    "1536×640  (12:5)"
                ]
            };

            const onModelChange = function (value, oldValue, node) {
                const aspect_ratio = node.widgets.find(w => w.name === "aspect_ratio");
                if (!aspect_ratio) return;

                // Skip for WAN model
                if (value === "WAN") return;

                // Get resolutions for the selected model
                const options = MODEL_PRESETS[value] || [];
                if (!options.length) return;

                // Keep track of current value
                const currentValue = aspect_ratio.value;
                const defaultValue = "1024×1024  (1:1)";

                // Update available options
                aspect_ratio.options.values = options;

                // Keep current value if valid, otherwise use default or first option
                if (!options.includes(currentValue)) {
                    aspect_ratio.value = options.includes(defaultValue) ? defaultValue : options[0];
                }

                // Force widget to update
                requestAnimationFrame(() => {
                    aspect_ratio.callback?.(aspect_ratio.value);
                });
            };

            // Override the onNodeCreated callback
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                // Find the model widget and add our callback
                const modelWidget = this.widgets.find(w => w.name === "model");
                if (modelWidget) {
                    modelWidget.callback = onModelChange;
                    // Initial update of aspect ratio options
                    onModelChange(modelWidget.value, null, this);
                }

                return r;
            };
        }
    },
});
