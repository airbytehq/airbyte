/**
 * Swizzled DropdownNavbarItem/Desktop component.
 *
 * Adds route-based "active" styling to the dropdown parent label so that
 * "Data Replication" is underlined whenever the user is viewing any of its
 * child doc instances (Platform, Connectors, Release Notes, Developers,
 * Community).
 *
 * The only behavioural change vs. the upstream component is the
 * `containsActivePage` check and the conditional `navbar__link--active` class.
 */

import React, { useState, useRef, useEffect } from "react";
import clsx from "clsx";
import { useLocation } from "@docusaurus/router";
import NavbarNavLink from "@theme/NavbarItem/NavbarNavLink";
import NavbarItem from "@theme/NavbarItem";

/**
 * Route prefixes that belong to the "Data Replication" product area.
 * Defined here so only this component needs updating if routes change.
 */
const DATA_REPLICATION_PREFIXES = [
  "/platform",
  "/integrations",
  "/release_notes",
  "/developers",
  "/community",
];

/**
 * Returns true when the current pathname falls under any of the Data
 * Replication doc instances listed above.
 */
function useIsDataReplicationActive() {
  const { pathname } = useLocation();
  return DATA_REPLICATION_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(prefix + "/")
  );
}

export default function DropdownNavbarItemDesktop({
  items,
  position,
  className,
  onClick,
  ...props
}) {
  const dropdownRef = useRef(null);
  const [showDropdown, setShowDropdown] = useState(false);

  // Detect whether any child page is active so we can highlight the parent.
  const containsActivePage = useIsDataReplicationActive();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        !dropdownRef.current ||
        dropdownRef.current.contains(event.target)
      ) {
        return;
      }
      setShowDropdown(false);
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("touchstart", handleClickOutside);
    document.addEventListener("focusin", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("touchstart", handleClickOutside);
      document.removeEventListener("focusin", handleClickOutside);
    };
  }, [dropdownRef]);

  return (
    <div
      ref={dropdownRef}
      className={clsx("navbar__item", "dropdown", "dropdown--hoverable", {
        "dropdown--right": position === "right",
        "dropdown--show": showDropdown,
      })}
    >
      <NavbarNavLink
        aria-haspopup="true"
        aria-expanded={showDropdown}
        role="button"
        href={props.to ? undefined : "#"}
        className={clsx("navbar__link", className, {
          "navbar__link--active": containsActivePage,
        })}
        {...props}
        onClick={props.to ? undefined : (e) => e.preventDefault()}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            setShowDropdown(!showDropdown);
          }
        }}
      >
        {props.children ?? props.label}
      </NavbarNavLink>
      <ul className="dropdown__menu">
        {items.map((childItemProps, i) => (
          <NavbarItem
            isDropdownItem
            activeClassName="dropdown__link--active"
            {...childItemProps}
            key={i}
          />
        ))}
      </ul>
    </div>
  );
}
