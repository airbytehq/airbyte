import React, { useState } from "react";
import styles from "./AiAgentsHome.module.css";

const TABS = [
  {
    id: "sdk",
    label: "Python SDK",
    command: "uv add airbyte-agent-sdk",
    description: "Add the SDK to your Python project.",
    docsLink: "/ai-agents/get-started/developer-quickstart/",
    docsLabel: "Quickstart tutorials",
  },
  {
    id: "mcp",
    label: "MCP",
    command:
      "https://api.airbyte.com/mcp/v1/sse?client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET",
    description: "Paste this URL into your MCP client config.",
    docsLink: "/ai-agents/interfaces/mcp/",
    docsLabel: "MCP setup guide",
  },
  {
    id: "webapp",
    label: "Web app",
    command: null,
    description:
      "Chat with an AI agent in your browser. No code, no install.",
    docsLink: "https://app.airbyte.ai",
    docsLabel: "Open the web app",
  },
];

export const QuickInstall = () => {
  const [activeTab, setActiveTab] = useState("sdk");
  const [copied, setCopied] = useState(false);
  const tab = TABS.find((t) => t.id === activeTab);

  const handleCopy = () => {
    if (tab.command) {
      navigator.clipboard.writeText(tab.command);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className={styles.quickInstall}>
      <h2 className={styles.sectionHeading}>Get started</h2>
      <div className={styles.quickInstallTabs}>
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`${styles.quickInstallTab} ${
              activeTab === t.id ? styles.quickInstallTabActive : ""
            }`}
            onClick={() => {
              setActiveTab(t.id);
              setCopied(false);
            }}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div className={styles.quickInstallBody}>
        {tab.command && (
          <div className={styles.quickInstallCode}>
            <code>{tab.command}</code>
            <button
              className={styles.quickInstallCopy}
              onClick={handleCopy}
              aria-label="Copy to clipboard"
            >
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
        )}
        <p className={styles.quickInstallDescription}>{tab.description}</p>
        <a className={styles.quickInstallLink} href={tab.docsLink}>
          {tab.docsLabel} &rarr;
        </a>
      </div>
    </div>
  );
};
