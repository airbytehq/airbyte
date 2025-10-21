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
          id: "deprecated-list-embedded-source-templates",
          label: "List Source Templates",
          className: "menu__list-item--deprecated api-method post",
        },
        {
          type: "doc",
          id: "list-embedded-source-templates",
          label: "List Source Templates",
          className: "api-method get",
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
          id: "create-embedded-sources-check",
          label: "Run Check Config Source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-embedded-sources-check-id-status",
          label: "Status Check Config Source",
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
          id: "create-embedded-widget-token",
          label: "Create Widget Token",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-embedded-scoped-token",
          label: "Create Scoped Token",
          className: "api-method post",
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
        {
          type: "doc",
          id: "deprecated-get-embedded-scoped-token-info",
          label: "Get Scoped Token Info",
          className: "menu__list-item--deprecated api-method get",
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
          id: "list-sonar-files-source-id-drives-drive-id-list-path-path",
          label: "List Drive Files With Prefix",
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
          id: "get-sonar-files-source-id-drives-drive-id-get-path-path",
          label: "Drive Stream File",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "get-sonar-files-sources",
          label: "List Sources",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "get-sonar-files-source-id-drives",
          label: "List Drives",
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
        {
          type: "doc",
          id: "create-integrations-sources-check",
          label: "Run Check Config Source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-integrations-sources-check-id-status",
          label: "Status Check Config Source",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "get-integrations-sources-id-discover",
          label: "Get Source Catalog",
          className: "api-method get",
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
          id: "update-integrations-templates-connections-id",
          label: "Patch Connection Template",
          className: "api-method patch",
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
        {
          type: "doc",
          id: "create-integrations-templates-connections-id-tag",
          label: "Tag Connection Template",
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
          id: "update-integrations-templates-sources-id",
          label: "Update Source Template",
          className: "api-method patch",
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
        {
          type: "doc",
          id: "list-integrations-templates-sources-global",
          label: "List Global Source Templates",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "create-integrations-templates-sources-id-tag",
          label: "Tag Source Template",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "Tool Wrappers - Workspaces",
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "list-tools-workspaces",
          label: "List Workspaces",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Tool Wrappers - Destinations",
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "create-tools-destinations",
          label: "Tools Create Destination",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-tools-destinations-id",
          label: "Tools Update Destination",
          className: "api-method patch",
        },
      ],
    },
    {
      type: "category",
      label: "Tool Wrappers - Sources",
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "create-tools-sources",
          label: "Tools Create Source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-tools-sources-id",
          label: "Tools Update Source",
          className: "api-method patch",
        },
      ],
    },
    {
      type: "category",
      label: "Destinations Definitions",
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "get-integrations-definitions-destinations-id",
          label: "Get Destination Definition",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "list-integrations-definitions-destinations",
          label: "List Destination Definitions",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Sources Definitions",
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "get-integrations-definitions-sources-id",
          label: "Get Source Definition",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "create-integrations-definitions-sources-id-catalog",
          label: "Create Source Definition Catalog",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-integrations-definitions-sources-id-catalog",
          label: "Delete Source Definition Catalog",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "get-integrations-definitions-sources-id-catalog",
          label: "Get Source Definition Catalog",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Destinations",
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "list-integrations-destinations",
          label: "List Destinations",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "get-integrations-destinations-id",
          label: "Get Destination",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Template Tags",
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "create-integrations-templates-tags",
          label: "Create Template Tag",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-integrations-templates-tags",
          label: "List Template Tags",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "update-integrations-templates-tags-name",
          label: "Update Template Tag",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "delete-integrations-templates-tags-name",
          label: "Delete Template Tag",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "Health",
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "get-internal-health-check",
          label: "Health Check",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Organizations",
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "list-internal-account-organizations",
          label: "List Organizations",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "create-internal-account-organizations-id-onboarding-progress",
          label: "Update Organization Onboarding Progress",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "Applications",
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "create-internal-account-applications",
          label: "Get Or Create Application",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-internal-account-applications-token",
          label: "Generate Application Token",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "OAuth",
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "create-internal-oauth-mcp-registration",
          label: "Oauth Registration",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-internal-oauth-mcp-code",
          label: "Oauth Code",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-internal-oauth-mcp-token",
          label: "Oauth Token",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "OAuth - Sources",
      collapsible: false,
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "create-internal-oauth-sources-get-embedded-consent-url",
          label: "Get Embedded Consent Url",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-internal-oauth-sources-complete",
          label: "Complete Oauth",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-internal-oauth-sources-revoke",
          label: "Revoke Source Oauth",
          className: "api-method post",
        },
      ],
    },
  ],
};

export default sidebar.apisidebar;
