export default {
  embedded: [
    {
      type: "category",
      collapsible: false,
      label: "Airbyte Embedded",
      link: {
        type: "doc",
        id: "README",
      },
      items: [
        {
          type: "category",
          label: "PyAirbyte MCP",
          items: [
            "pyairbyte-mcp/README",
          ],
        },
        {
          type: "category",
          label: "Airbyte Embedded",
          items: [
            {
              type: "category",
              label: "Airbyte Widget",
              items: [
        "embedded/widget/prerequisites-setup",
        "embedded/widget/develop-your-app",
        "embedded/widget/use-embedded",
        "embedded/widget/managing-embedded",
              ],
            },
            {
              type: "category",
              label: "Embedded API",
              items: [
                "embedded/api/connection-templates",
                "embedded/api/source-templates",
              ],
            },
          ],
        },
        {
          type: "link",
          label: "API Reference",
          href: "/embedded-api/airbyte-embedded-api",
        },
      ],
    },
  ],
};
