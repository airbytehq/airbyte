const sectionHeader = (title) => ({
  type: "html",
  value: title,
  className: "navbar__category",
});

const contributeToAirbyte = {
  type: "category",
  label: "Contribute to Airbyte",
  link: {
    type: "doc",
    id: "contributing-to-airbyte/README",
  },
  items: [
    "contributing-to-airbyte/issues-and-requests",
    "contributing-to-airbyte/developing-locally",
    "contributing-to-airbyte/writing-docs",
    {
      type: "category",
      label: "Resources",
      items: [
        "contributing-to-airbyte/resources/pull-requests-handbook",
        "contributing-to-airbyte/resources/qa-checks",
      ],
    },
  ],
};

module.exports = {
  community: [
    {
      type: "category",
      collapsible: false,
      label: "Community & Support",
      items: [
        "getting-support",
        contributeToAirbyte,
        "code-of-conduct",
        {
          type: "link",
          label: "Roadmap",
          href: "https://go.airbyte.com/roadmap",
        },
      ],
    },
  ],
};
