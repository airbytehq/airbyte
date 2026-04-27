/**
 * Remark plugin that groups adjacent fenced code blocks sharing the same
 * language into a Docusaurus <Tabs>/<TabItem> component, using each block's
 * `title` metadata as the tab label.
 *
 * The Jinja templates in sonar emit sequential code blocks like:
 *
 *   **Pydantic AI**
 *   ```python title="Pydantic AI"
 *   ...
 *   ```
 *   **LangChain**
 *   ```python title="LangChain"
 *   ...
 *   ```
 *
 * On GitHub these render as labeled code blocks (readable, just longer).
 * This plugin transforms them into tabbed UI in Docusaurus.
 *
 * The bold label paragraph preceding each code block is consumed into the
 * tab so it doesn't appear as duplicate text.
 */

/**
 * Parse the `meta` string of a code node to extract a `title="..."` value.
 */
function extractTitle(meta) {
  if (!meta) return null;
  const match = meta.match(/title="([^"]+)"/);
  return match ? match[1] : null;
}

/**
 * Check if a node is a paragraph containing only bold text matching `label`.
 * Handles both `strong > text` (markdown **label**) patterns.
 */
function isBoldLabelParagraph(node, label) {
  if (node.type !== "paragraph" || node.children.length !== 1) return false;
  const child = node.children[0];
  if (child.type !== "strong" || child.children.length !== 1) return false;
  return child.children[0].type === "text" && child.children[0].value === label;
}

function buildTabsImport() {
  return [
    {
      type: "mdxjsEsm",
      value: 'import Tabs from "@theme/Tabs";',
      data: {
        estree: {
          type: "Program",
          sourceType: "module",
          body: [
            {
              type: "ImportDeclaration",
              source: { type: "Literal", value: "@theme/Tabs" },
              specifiers: [
                {
                  type: "ImportDefaultSpecifier",
                  local: { type: "Identifier", name: "Tabs" },
                },
              ],
            },
          ],
        },
      },
    },
    {
      type: "mdxjsEsm",
      value: 'import TabItem from "@theme/TabItem";',
      data: {
        estree: {
          type: "Program",
          sourceType: "module",
          body: [
            {
              type: "ImportDeclaration",
              source: { type: "Literal", value: "@theme/TabItem" },
              specifiers: [
                {
                  type: "ImportDefaultSpecifier",
                  local: { type: "Identifier", name: "TabItem" },
                },
              ],
            },
          ],
        },
      },
    },
  ];
}

function buildTabItem(title, codeNode, isDefault) {
  const slug = title.toLowerCase().replace(/\s+/g, "-");
  const attrs = [
    { type: "mdxJsxAttribute", name: "value", value: slug },
    { type: "mdxJsxAttribute", name: "label", value: title },
  ];
  if (isDefault) {
    attrs.push({ type: "mdxJsxAttribute", name: "default", value: null });
  }
  return {
    type: "mdxJsxFlowElement",
    name: "TabItem",
    attributes: attrs,
    children: [codeNode],
  };
}

function buildTabs(tabItems) {
  return {
    type: "mdxJsxFlowElement",
    name: "Tabs",
    attributes: [],
    children: tabItems,
  };
}

const plugin = () => {
  const transformer = (ast) => {
    let needsImport = false;
    const children = ast.children;
    let i = 0;

    while (i < children.length) {
      const node = children[i];

      // Look for a code block with a title
      if (node.type !== "code" || !extractTitle(node.meta)) {
        i++;
        continue;
      }

      // Collect a run of titled code blocks (with optional bold label paragraphs)
      const group = [];
      let j = i;

      while (j < children.length) {
        const current = children[j];

        if (current.type === "code" && extractTitle(current.meta)) {
          const title = extractTitle(current.meta);
          // Check if previous node is a bold label for this code block
          const prevIdx = group.length > 0 ? j - 1 : i - 1;
          let labelNodeIdx = null;
          if (
            prevIdx >= 0 &&
            prevIdx < children.length &&
            isBoldLabelParagraph(children[prevIdx], title)
          ) {
            labelNodeIdx = prevIdx;
          }
          group.push({ codeIdx: j, labelIdx: labelNodeIdx, title });
          j++;
          continue;
        }

        // A bold label paragraph might precede the next code block
        if (
          current.type === "paragraph" &&
          j + 1 < children.length &&
          children[j + 1].type === "code" &&
          extractTitle(children[j + 1].meta)
        ) {
          const nextTitle = extractTitle(children[j + 1].meta);
          if (isBoldLabelParagraph(current, nextTitle)) {
            // Skip the label — it will be consumed with the next code block
            j++;
            continue;
          }
        }

        // Anything else breaks the group
        break;
      }

      // Need at least 2 titled blocks to form tabs
      if (group.length < 2) {
        i++;
        continue;
      }

      // Build tab items
      const tabItems = group.map((entry, idx) =>
        buildTabItem(entry.title, children[entry.codeIdx], idx === 0),
      );
      const tabsNode = buildTabs(tabItems);

      // Calculate the range of nodes to replace (from first label/code to last code)
      const allIndices = [];
      for (const entry of group) {
        if (entry.labelIdx !== null) allIndices.push(entry.labelIdx);
        allIndices.push(entry.codeIdx);
      }
      // Also include any label-only nodes between code blocks
      const startIdx = Math.min(...allIndices);
      const endIdx = j; // j is one past the last node in the group

      children.splice(startIdx, endIdx - startIdx, tabsNode);
      needsImport = true;

      // Continue scanning from just after the tabs node
      i = startIdx + 1;
    }

    if (needsImport) {
      ast.children.unshift(...buildTabsImport());
    }
  };

  return transformer;
};

module.exports = plugin;
