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
              ]
            },
            "embedded/widget/managing-embedded",
            "embedded/widget/template-tags",
          ]
        },
        {
          type: "category",
          label: "API",
          items: [
            "embedded/api/README",
            "embedded/api/connection-templates",
            "embedded/api/source-templates",
            "embedded/api/configuring-sources",
          ]
        },

          ]
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
              id: "pyairbyte-fast-coder-mcp",
              label: "PyAirbyte Fast-Coder MCP",
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
