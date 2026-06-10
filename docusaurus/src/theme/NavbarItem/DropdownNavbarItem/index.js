/**
 * Swizzled DropdownNavbarItem wrapper.
 * Routes to the custom Desktop component (which adds active-state detection)
 * or falls back to the upstream Mobile component.
 */

import React from "react";
import DropdownNavbarItemMobile from "@theme-original/NavbarItem/DropdownNavbarItem/Mobile";
import DropdownNavbarItemDesktop from "./Desktop";

export default function DropdownNavbarItem({ mobile = false, ...props }) {
  const Comp = mobile ? DropdownNavbarItemMobile : DropdownNavbarItemDesktop;
  return <Comp {...props} />;
}
