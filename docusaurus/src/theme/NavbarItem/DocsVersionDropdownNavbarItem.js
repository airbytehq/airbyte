import React from "react";
import DocsVersionDropdownNavbarItem from "@theme-original/NavbarItem/DocsVersionDropdownNavbarItem";
import { useLocation } from "@docusaurus/router";

export default function DocsVersionDropdownNavbarItemWrapper(props) {
  const { docsPluginId, className, type } = props;
  const { pathname } = useLocation();

  // Check if the docsPluginId property for this instance contains the URL pathname. If it does, show the version dropdown. If it doesn't, don't show it. This is a workaround for the fact that Docusaurus shows the version dropdown for all instances of the DocsVersionDropdownNavbarItem component, even if the current page or instance is not versioned.

  // Swizzling this component is technically unsafe, although the risk is very low. Worst-case scenario, we have to upgrade it ourselves in a future breaking change with Docusaurus.

  const doesPathnameContainDocsPluginId = pathname.includes(docsPluginId);
  if (!doesPathnameContainDocsPluginId) {
    return null;
  }
  return <DocsVersionDropdownNavbarItem {...props} />;
}
