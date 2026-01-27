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
    "contributing-to-airbyte/resources/pull-requests-handbook",
    "contributing-to-airbyte/resources/qa-checks",
  ],
};

const licenses = {
  type: "category",
  label: "Licenses",
  link: {
    type: "doc",
    id: "licenses/README",
  },
  items: [
    "licenses/license-faq",
    "licenses/elv2-license",
    "licenses/mit-license",
    "licenses/examples",
  ],
};

module.exports = {
  community: [
    {
      type: "category",
      collapsible: false,
      label: "Community & support",
      link: {
        type: "doc",
        id: "README",
      },
      items: [
        "getting-support",
        contributeToAirbyte,
        "code-of-conduct",
        licenses,
        {
          type: "link",
          label: "Public roadmap",
          href: "https://go.airbyte.com/roadmap",
        },
      ],
    },
  ],
};
