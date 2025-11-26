import apiSidebarItems from "../docs/ai-agents/embedded/api-reference/sidebar.ts";

// Helper function to add unique keys to sidebar items to avoid duplicate translation key errors
// The generated sidebar already has correct IDs, we just need to add unique keys
function addUniqueKeys(items) {
  return items.map((item) => {
    if (item.type === "doc") {
      return {
        ...item,
        // Use the doc id as a unique translation key
        key: item.id,
      };
    }

    if (item.type === "category") {
      return {
        ...item,
        // Make categories unique too using their link id or label
        key: item.link?.id || item.label,
        items: item.items ? addUniqueKeys(item.items) : [],
      };
    }

    return item;
  });
}

// Get the generated API sidebar items with unique keys
// Skip the first item (sonar overview) since we use it as the category link
const [, ...apiSidebarItemsWithKeys] = addUniqueKeys(apiSidebarItems);

export default {
  "ai-agents": [
    {
      type: "category",
      collapsible: false,
      label: "AI Agents",
      link: {
        type: "doc",
        id: "README",
      },
      items: [
        {
          type: "category",
          label: "Embedded",
          items: [
            {
              type: "category",
              label: "Widget",
              items: [
                "embedded/widget/quickstart",
                {
                  type: "category",
                  label: "Tutorials",
                  items: [
                    "embedded/widget/tutorials/prerequisites-setup",
                    "embedded/widget/tutorials/develop-your-app",
                    "embedded/widget/tutorials/use-embedded",
                  ],
                },
                "embedded/widget/managing-embedded",
                "embedded/widget/template-tags",
              ],
            },
            {
              type: "category",
              label: "API",
              items: [
                "embedded/api/README",
                {
                  type: "category",
                  label: "Sonar API Reference",
                  link: {
                    type: "doc",
                    id: "embedded/api-reference/sonar",
                  },
                  items: apiSidebarItemsWithKeys,
                },
                "embedded/api/connection-templates",
                "embedded/api/source-templates",
                "embedded/api/configuring-sources",
              ],
            },
          ],
        },
        {
          type: "category",
          label: "MCP Servers",
          items: [
            {
              type: "doc",
              id: "pyairbyte-mcp",
              label: "PyAirbyte MCP",
            },
            {
              type: "doc",
              id: "connector-builder-mcp",
              label: "Connector Builder MCP",
            },
            {
              type: "doc",
              id: "embedded/operator-mcp/README",
              label: "Embedded Operator MCP",
            }
          ]
        }
      ]
    }
  ],
};
