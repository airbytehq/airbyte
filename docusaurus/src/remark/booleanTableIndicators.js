const visit = require("unist-util-visit").visit;

const BOOLEAN_MARKERS = new Map([
  ["yes", { label: "Yes", status: "supported" }],
  ["no", { label: "No", status: "unsupported" }],
  ["supported", { label: "Supported", status: "supported" }],
  ["not supported", { label: "Not supported", status: "unsupported" }],
  ["✅", { label: "Supported", status: "supported" }],
  ["❌", { label: "Not supported", status: "unsupported" }],
]);

const getMarker = (cell) => {
  if (!cell || !Array.isArray(cell.children) || cell.children.length !== 1) {
    return null;
  }

  const child = cell.children[0];
  if (child.type !== "text" || typeof child.value !== "string") {
    return null;
  }

  return BOOLEAN_MARKERS.get(child.value.trim().toLowerCase()) || null;
};

const plugin = () => {
  const transformer = (ast) => {
    visit(ast, "table", (table) => {
      if (!Array.isArray(table.children)) return;

      table.children.slice(1).forEach((row) => {
        if (!row || !Array.isArray(row.children)) return;

        row.children.forEach((cell) => {
          if (!cell || cell.type !== "tableCell") return;

          const marker = getMarker(cell);
          if (!marker) return;

          cell.children = [
            {
              type: "mdxJsxTextElement",
              name: "BooleanTableIndicator",
              attributes: [
                {
                  type: "mdxJsxAttribute",
                  name: "label",
                  value: marker.label,
                },
                {
                  type: "mdxJsxAttribute",
                  name: "status",
                  value: marker.status,
                },
              ],
              children: [],
            },
          ];
        });
      });
    });
  };

  return transformer;
};

module.exports = plugin;
