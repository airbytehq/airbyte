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
  // Exact match for trailing-slash items
  if (pathname === href || pathname === href.replace(/\/$/, "")) {
    return true;
  }
  // Prefix match
  return pathname.startsWith(href);
}

export default function NavbarWrapper(props) {
  const { pathname } = useLocation();
  const isAgentEngine = isAgentEnginePath(pathname);
  const isDataReplication = isDataReplicationPath(pathname);
  const isHome = pathname === "/";

  // Determine which top-level tab is active
  const activeTopTab = isAgentEngine
    ? "agent-engine"
    : isDataReplication || isHome
      ? "data-replication"
      : "data-replication";

  return (
    <>
      <Navbar {...props} />
      <div className={styles.secondaryNavWrapper}>
        <div className={styles.secondaryNav}>
          {/* Top-level platform tabs */}
          <div className={styles.platformTabs}>
            <a
              href="/platform/"
              className={`${styles.platformTab} ${activeTopTab === "data-replication" ? styles.platformTabActive : ""}`}
            >
              Data Replication
            </a>
            <a
              href="/ai-agents/"
              className={`${styles.platformTab} ${activeTopTab === "agent-engine" ? styles.platformTabActive : ""}`}
            >
              Agent Engine
            </a>
          </div>

          {/* Secondary nav items - only shown for Data Replication */}
          {activeTopTab === "data-replication" && (
            <div className={styles.secondaryItems}>
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
          )}
        </div>
      </div>
    </>
  );
}
