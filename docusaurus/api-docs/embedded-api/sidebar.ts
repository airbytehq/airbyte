import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

const sidebar: SidebarsConfig = {
  apisidebar: [
    {
      type: "doc",
      id: "sonar",
    },
    {
      type: "category",
      label: "Embedded",
      link: {
        type: "doc",
        id: "embedded",
      },
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "list-embedded-source-templates",
          label: "List Source Templates",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-embedded-source-templates-id",
          label: "Get Source Template",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "create-embedded-sources",
          label: "Create Source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-embedded-sources",
          label: "List Sources",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "get-embedded-sources-id",
          label: "Get Source",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "update-embedded-sources-id",
          label: "Update Source",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "delete-embedded-sources-id",
          label: "Delete Source",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "create-embedded-scoped-token",
          label: "Create Scoped Token",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "deprecated-get-embedded-scoped-token-info",
          label: "Get Scoped Token Info",
          className: "menu__list-item--deprecated api-method get",
        },
        {
          type: "doc",
          id: "deprecated-get-embedded-organizations-current-scoped",
          label: "Get Scoped Token Info",
          className: "menu__list-item--deprecated api-method get",
        },
        {
          type: "doc",
          id: "get-embedded-scoped-token-info",
          label: "Get Scoped Token Info",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Sonar - APIs",
      link: {
        type: "doc",
        id: "sonar-ap-is",
      },
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "create-sonar-apis-source-id-request",
          label: "Request",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "deprecated-get-sonar-apis",
          label: "List Sources",
          className: "menu__list-item--deprecated api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Sonar - Files",
      link: {
        type: "doc",
        id: "sonar-files",
      },
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "list-sonar-files-source-id-list-path-path",
          label: "List Files With Prefix",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "get-sonar-files-source-id-get-path-path",
          label: "Stream File",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "get-sonar-files-sources",
          label: "List Sources",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Sources",
      link: {
        type: "doc",
        id: "sources",
      },
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "create-integrations-sources",
          label: "Create Source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-integrations-sources",
          label: "List Sources",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "get-integrations-sources-id",
          label: "Get Source",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "update-integrations-sources-id",
          label: "Update Source",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "delete-integrations-sources-id",
          label: "Delete Source",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "Template Connections",
      link: {
        type: "doc",
        id: "template-connections",
      },
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "get-integrations-templates-connections-id",
          label: "Get Connection Template",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "delete-integrations-templates-connections-id",
          label: "Delete Connection Template",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "list-integrations-templates-connections",
          label: "List Connection Templates",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "create-integrations-templates-connections",
          label: "Create Connection Template",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "Template Sources",
      link: {
        type: "doc",
        id: "template-sources",
      },
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "create-integrations-templates-sources",
          label: "Create Source Template",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-integrations-templates-sources",
          label: "List Source Templates",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "get-integrations-templates-sources-id",
          label: "Get Source Template",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "delete-integrations-templates-sources-id",
          label: "Delete Source Templates",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "Deprecation Corner",
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "deprecated-create-embedded-partial-user-configs",
          label: "[Deprecated] Api Create Source",
          className: "menu__list-item--deprecated api-method post",
        },
        {
          type: "doc",
          id: "deprecated-list-embedded-partial-user-configs",
          label: "[Deprecated] Api List Sources",
          className: "menu__list-item--deprecated api-method get",
        },
        {
          type: "doc",
          id: "deprecated-get-embedded-partial-user-configs-id",
          label: "[Deprecated] Api Get Source",
          className: "menu__list-item--deprecated api-method get",
        },
        {
          type: "doc",
          id: "deprecated-update-embedded-partial-user-configs-id",
          label: "[Deprecated] Api Update Source",
          className: "menu__list-item--deprecated api-method put",
        },
        {
          type: "doc",
          id: "deprecated-delete-embedded-partial-user-configs-id",
          label: "[Deprecated] Api Delete Source",
          className: "menu__list-item--deprecated api-method delete",
        },
      ],
    },
  ],
};

export default sidebar.apisidebar;
