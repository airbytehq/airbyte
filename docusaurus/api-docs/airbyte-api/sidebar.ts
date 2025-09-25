import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

const sidebar: SidebarsConfig = {
  apisidebar: [
    {
      type: "doc",
      id: "airbyte-sources-api",
    },
    {
      type: "category",
      label: "Sources",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "list-sources",
          label: "List Sources",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "create-source",
          label: "Create Source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-source",
          label: "Get Source",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "public_sources",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "list-sources",
          label: "List Sources",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "create-source",
          label: "Create Source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-source",
          label: "Get Source",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "public",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "list-sources",
          label: "List Sources",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "create-source",
          label: "Create Source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-source",
          label: "Get Source",
          className: "api-method get",
        },
      ],
    },
  ],
};

export default sidebar.apisidebar;
