export default {
  "developer-tools": [
    { 
      type: "category",
      collapsible: false,
      label: "Developer Tools",
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
            "prerequisites-setup",
            "develop-your-app",
            "use-embedded",
            "managing-embedded",
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
          type: "doc",
          id: "pyairbyte-mcp/README",
          label: "PyAirbyte MCP",
        },
        {
          type: "doc",
          id: "authentication-proxy/README",
          label: "Authentication Proxy",
        }
      ]
    }
  ],
};
