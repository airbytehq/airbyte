const sectionHeader = (title) => ({
  type: "html",
  value: title,
  className: "navbar__category",
});

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
        "get-an-application-key",
        "api-documentation",
        "terraform-documentation",
        {
          type: "doc",
          label: "Using PyAirbyte",
          id: "using-pyairbyte",
        },
      ],
    },
  ],
};
