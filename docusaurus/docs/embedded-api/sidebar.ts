const sidebar = {
  apisidebar: [
    {
      type: "doc",
      id: "sonar-api",
    },
    {
      type: "category",
      label: "Source Config Template",
      link: {
        type: "doc",
        id: "source-config-template",
      },
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "embedded-create-source-config-template",
          label: "Create Source Config Template",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "embedded-list-source-config-templates",
          label: "List Source Config Templates",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "embedded-get-source-config-template",
          label: "Get Source Config Template",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Connection Config Template",
      link: {
        type: "doc",
        id: "connection-config-template",
      },
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "embedded-get-connection-config-template",
          label: "Get Connection Config Template",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "embedded-delete-connection-config-template",
          label: "Delete Connection Config Template",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "embedded-create-connection-config-template",
          label: "Create Connection Config Template",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "Partial User Config",
      link: {
        type: "doc",
        id: "partial-user-config",
      },
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "embedded-create-partial-user-config",
          label: "Create Partial User Config",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "embedded-list-partial-user-configs",
          label: "List Partial User Configs",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "embedded-get-partial-user-config",
          label: "Get Partial User Config",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "embedded-update-partial-user-config",
          label: "Update Partial User Config",
          className: "api-method put",
        },
      ],
    },
    {
      type: "category",
      label: "Organizations",
      link: {
        type: "doc",
        id: "organizations",
      },
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "embedded-list-embedded-organizations",
          label: "List Embedded Organizations",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "embedded-get-current-scoped-organization",
          label: "Get Current Scoped Organization",
          className: "api-method get",
        },
      ],
    },
  ],
};

export default sidebar.apisidebar;
