import React from "react";
import DocsVersionDropdownNavbarItem from "@theme-original/NavbarItem/DocsVersionDropdownNavbarItem";
import { useLocation } from "@docusaurus/router";

export default function DocsVersionDropdownNavbarItemWrapper(props) {
  const { docsPluginId, className, type } = props;
  const { pathname } = useLocation();

  // Check if the current page belongs to this docs plugin by verifying the pathname
  // starts with the plugin's route base path (e.g. "/platform/"). Using a prefix check
  // instead of a substring match avoids false positives like "/ai-agents/platform/"
  // matching the "platform" plugin.

  // Swizzling this component is technically unsafe, although the risk is very low. Worst-case scenario, we have to upgrade it ourselves in a future breaking change with Docusaurus.

  const pluginBasePath = `/${docsPluginId}/`;
  const isOnPluginPage =
    pathname.startsWith(pluginBasePath) || pathname === `/${docsPluginId}`;
  if (!isOnPluginPage) {
    return null;
  }
  return <DocsVersionDropdownNavbarItem {...props} />;
}
