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
    tools: [
      {
        name: "Pydantic AI",
        href: "/ai-agents/get-started/developer-quickstart/tutorial-pydantic",
        icon: "/img/ai-agents/pydantic.svg",
      },
      {
        name: "LangChain",
        href: "/ai-agents/get-started/developer-quickstart/tutorial-langchain",
        icon: "/img/ai-agents/langchain.svg",
      },
      {
        name: "FastMCP",
        href: "/ai-agents/get-started/developer-quickstart/tutorial-fastmcp",
        icon: "/img/ai-agents/fastmcp.svg",
      },
    ],
  },
  {
    id: "mcp",
    label: "MCP",
    command: "https://mcp.airbyte.ai/mcp",
    description: "Add this URL to your MCP client.",
    docsLink: "/ai-agents/interfaces/mcp/",
    docsLabel: "MCP setup guide",
    tools: [
      {
        name: "Claude",
        href: "/ai-agents/interfaces/mcp/",
        icon: "/img/ai-agents/anthropic.svg",
      },
      {
        name: "Cursor",
        href: "/ai-agents/interfaces/mcp/",
        icon: "/img/ai-agents/cursor.svg",
      },
      {
        name: "Windsurf",
        href: "/ai-agents/interfaces/mcp/",
        icon: "/img/ai-agents/windsurf.svg",
      },
      {
        name: "VS Code",
        href: "/ai-agents/interfaces/mcp/",
        icon: "/img/ai-agents/visualstudiocode.svg",
      },
    ],
  },
  {
    id: "webapp",
    label: "Web app",
    command: null,
    description:
      "Chat with an AI agent in your browser. No code, no install.",
    docsLink: "https://app.airbyte.ai",
    docsLabel: "Open the web app",
    tools: [],
  },
];

const SKILLS = [
  {
    name: "Claude Code",
    href: "/ai-agents/get-started/developer-quickstart/skills/claude-code",
    icon: "/img/ai-agents/anthropic.svg",
  },
  {
    name: "Codex",
    href: "/ai-agents/get-started/developer-quickstart/skills/codex",
    icon: "/img/ai-agents/openai.svg",
  },
  {
    name: "Lovable",
    href: "/ai-agents/get-started/developer-quickstart/skills/lovable",
    icon: "/img/ai-agents/lovable.svg",
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
        {tab.tools.length > 0 && (
          <div className={styles.toolChips}>
            {tab.tools.map((tool) => (
              <a key={tool.name} className={styles.toolChip} href={tool.href}>
                <img
                  className={styles.toolChipIcon}
                  src={tool.icon}
                  alt={tool.name}
                />
                <span>{tool.name}</span>
              </a>
            ))}
          </div>
        )}
      </div>
      <div className={styles.skillsSection}>
        <span className={styles.skillsLabel}>Agent skills</span>
        <div className={styles.skillsChips}>
          {SKILLS.map((skill) => (
            <a key={skill.name} className={styles.skillChip} href={skill.href}>
              <img
                className={styles.toolChipIcon}
                src={skill.icon}
                alt={skill.name}
              />
              <span>{skill.name}</span>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
};
