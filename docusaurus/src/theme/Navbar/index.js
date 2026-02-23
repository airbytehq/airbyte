import React from "react";
import Navbar from "@theme-original/Navbar";
import { useLocation } from "@docusaurus/router";
import styles from "./styles.module.css";

// The secondary nav items for "Data Replication" section
const dataReplicationItems = [
  { label: "Platform", href: "/platform/" },
  { label: "Connectors", href: "/integrations/" },
  { label: "Release Notes", href: "/release_notes/" },
  { label: "Developers", href: "/developers/" },
  { label: "Community", href: "/community/" },
];

// Route prefixes that belong to the Agent Engine section
const agentEnginePrefixes = ["/ai-agents"];

// Route prefixes that belong to the Data Replication section
const dataReplicationPrefixes = [
  "/platform",
  "/integrations",
  "/release_notes",
  "/developers",
  "/community",
];

function isAgentEnginePath(pathname) {
  return agentEnginePrefixes.some((prefix) => pathname.startsWith(prefix));
}

function isDataReplicationPath(pathname) {
  return dataReplicationPrefixes.some((prefix) => pathname.startsWith(prefix));
}

function isSecondaryItemActive(href, pathname) {
  if (pathname === href || pathname === href.replace(/\/$/, "")) {
    return true;
  }
  return pathname.startsWith(href);
}

export default function NavbarWrapper(props) {
  const { pathname } = useLocation();
  const isAgentEngine = isAgentEnginePath(pathname);
  const isDataReplication = isDataReplicationPath(pathname);
  const isHome = pathname === "/";

  // Show secondary nav only for Data Replication pages and homepage.
  // "Data Replication" and "Agent Engine" tabs are now in the primary
  // navbar row (configured in docusaurus.config.ts), so the secondary
  // row only contains section-level links.
  const showSecondaryNav = !isAgentEngine && (isDataReplication || isHome);

  if (!showSecondaryNav) {
    return <Navbar {...props} />;
  }

  return (
    <div className={styles.primaryNavBorder}>
      <Navbar {...props} />
      <div className={styles.secondaryNavWrapper}>
        <div className={styles.secondaryNav}>
          {dataReplicationItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className={`${styles.secondaryItem} ${isSecondaryItemActive(item.href, pathname) ? styles.secondaryItemActive : ""}`}
            >
              {item.label}
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
