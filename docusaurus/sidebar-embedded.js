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
        "prerequisites-setup",
        "develop-your-app",
        "use-embedded",
        "managing-embedded",
        {
          type: "link",
          label: "API Reference",
          href: "/embedded-api/airbyte-embedded-api",
        },
      ],
    },
  ],
};
