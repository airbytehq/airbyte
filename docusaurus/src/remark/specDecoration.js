const visit = require("unist-util-visit").visit;
const { catalog } = require("../connector_registry");
const { isDocsPage, getRegistryEntry } = require("./utils");

const plugin = () => {
  const transformer = async (ast, vfile) => {
    await injectDefaultPyAirbyteSection(vfile, ast);
    await injectSpecSchema(ast);
  };
  return transformer;
};

async function injectSpecSchema(ast) {
  const registry = await catalog;
  visit(ast, "mdxJsxFlowElement", (node) => {
    if (node.name !== "SpecSchema" && node.name !== "PyAirbyteExample") return;

    const connectorName = node.attributes.find(
      (attr) => attr.name === "connector"
    ).value;
    const connectorSpec = registry.find(
      (c) => c.dockerRepository_oss === `airbyte/${connectorName}`
    ).spec_oss.connectionSpecification;
    node.attributes.push({
      type: "mdxJsxAttribute",
      name: "specJSON",
      value: JSON.stringify(connectorSpec),
    });
  });
}

async function injectDefaultPyAirbyteSection(vfile, ast) {
  const registryEntry = await getRegistryEntry(vfile);
  const docsPageInfo = isDocsPage(vfile);

  if (
    !docsPageInfo.isTrueDocsPage ||
    !registryEntry ||
    vfile.value.includes("## Usage with PyAirbyte")
  ) {
    return;
  }
  const connectorName = registryEntry.dockerRepository_oss.split("/").pop();
  const hasValidSpec = registryEntry.spec_oss && registryEntry.spec_oss.connectionSpecification;

  let added = false;
  visit(ast, "heading", (node, index, parent) => {
    if (!added && isChangelogHeading(node)) {
      added = true;
      const referenceContent = hasValidSpec ? [
        {
          type: "mdxJsxFlowElement",
          name: "SpecSchema",
          attributes: [
            {
              type: "mdxJsxAttribute",
              name: "connector",
              value: connectorName,
            },
          ],
        }
      ] : [
        {
          type: "paragraph",
          children: [
            {
              type: "text",
              value: "No configuration specification is available for this connector."
            }
          ]
        }
      ];

      parent.children.splice(
        index,
        0,
        {
          type: "heading",
          depth: 2,
          children: [{ type: "text", value: "Reference" }],
        },
        ...referenceContent
      );
    }
  });
  if (!added) {
    // If no Changelog heading found, try to find first h2 heading
    let firstH2Index = -1;
    visit(ast, "heading", (node, index) => {
      if (!added && node.depth === 2 && firstH2Index === -1) {
        firstH2Index = index;
      }
    });

    // Insert after first h2 if found
    if (firstH2Index >= 0) {
      visit(ast, "heading", (node, index, parent) => {
        if (index === firstH2Index) {
          added = true;
          const referenceContent = hasValidSpec ? [
            {
              type: "mdxJsxFlowElement",
              name: "SpecSchema",
              attributes: [
                {
                  type: "mdxJsxAttribute",
                  name: "connector",
                  value: connectorName,
                },
              ],
            }
          ] : [
            {
              type: "paragraph",
              children: [
                {
                  type: "text",
                  value: "No configuration specification is available for this connector."
                }
              ]
            }
          ];

          parent.children.splice(
            index + 1,
            0,
            {
              type: "heading",
              depth: 2,
              children: [{ type: "text", value: "Reference" }],
            },
            ...referenceContent
          );
        }
      });
    }

    // If still not added, append to end of document
    if (!added) {
      const referenceContent = hasValidSpec ? [
        {
          type: "mdxJsxFlowElement",
          name: "SpecSchema",
          attributes: [
            {
              type: "mdxJsxAttribute",
              name: "connector",
              value: connectorName,
            },
          ],
        }
      ] : [
        {
          type: "paragraph",
          children: [
            {
              type: "text",
              value: "No configuration specification is available for this connector."
            }
          ]
        }
      ];

      ast.children.push(
        {
          type: "heading",
          depth: 2,
          children: [{ type: "text", value: "Reference" }],
        },
        ...referenceContent
      );
    }
  }
}

function isChangelogHeading(node) {
  return (
    node.depth === 2 &&
    node.children.length === 1 &&
    node.children[0].value.toLowerCase() === "changelog"
  );
}

module.exports = plugin;
