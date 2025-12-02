module.exports = {
  developers: [
    {
      type: "category",
      collapsible: false,
      label: "Developers",
      link: {
        type: "doc",
        id: "README",
      },
      items: [
        "api-documentation",
        "terraform-documentation",
        {
          type: "doc",
          label: "PyAirbyte",
          id: "using-pyairbyte",
        },
        {
          type: 'link',
          label: 'Python SDK',
          href: 'https://github.com/airbytehq/airbyte-api-python-sdk',
        },
        {
          type: 'link',
          label: 'Java SDK',
          href: 'https://github.com/airbytehq/airbyte-api-java-sdk',
        },
      ],
    },
  ],
};
