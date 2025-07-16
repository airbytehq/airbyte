const sidebar = {
  apisidebar: [
    {
      type: "doc",
      id: "airbyte-embedded-api",
    },
    {
      type: "category",
      label: "connection_config_template",
      link: {
        type: "doc",
        id: "connection-config-template",
      },
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "embedded-config-templates-connections-id-get-connection-config-template",
          label: "Get Connection Config Template",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "embedded-config-templates-connections-id-delete-connection-config-template",
          label: "Delete Connection Config Template",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "embedded-config-templates-connections-list-connection-config-templates",
          label: "List Connection Config Templates",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "embedded-config-templates-connections-create-connection-config-template",
          label: "Create Connection Config Template",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "source_config_template",
      link: {
        type: "doc",
        id: "source-config-template",
      },
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "embedded-config-templates-sources-create-source-config-template",
          label: "Create Source Config Template",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "embedded-config-templates-sources-list-source-config-templates",
          label: "List Source Config Templates",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "embedded-config-templates-sources-id-get-source-config-template",
          label: "Get Source Config Template",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "partial_user_config",
      link: {
        type: "doc",
        id: "partial-user-config",
      },
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "embedded-partial-user-configs-create-partial-user-config",
          label: "Create Partial User Config",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "embedded-partial-user-configs-list-partial-user-configs",
          label: "List Partial User Configs",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "embedded-partial-user-configs-id-get-partial-user-config",
          label: "Get Partial User Config",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "embedded-partial-user-configs-id-update-partial-user-config",
          label: "Update Partial User Config",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "embedded-partial-user-configs-id-delete-partial-user-config",
          label: "Delete Partial User Config",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "organizations",
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "embedded-organizations-list-embedded-organizations",
          label: "List Embedded Organizations",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "embedded-organizations-current-scoped-get-current-scoped-organization",
          label: "Get Current Scoped Organization",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "embedded-organizations-id-onboarding-progress-update-organization-onboarding-progress",
          label: "Update Organization Onboarding Progress",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "api_sources",
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "proxy-api-sources-source-id-passthrough-passthrough",
          label: "Passthrough",
          className: "api-method post",
        },
      ],
    },
  ],
};

export default sidebar.apisidebar;
