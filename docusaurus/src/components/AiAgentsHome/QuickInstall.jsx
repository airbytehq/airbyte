import React, { useState } from "react";
import styles from "./AiAgentsHome.module.css";

const TABS = [
  {
    id: "mcp",
    label: "MCP",
    command: "https://mcp.airbyte.ai/mcp",
    description: "Add this URL to your MCP client.",
    tools: [
      {
        name: "Claude",
        href: "/ai-agents/interfaces/mcp/",
        icon: "/img/ai-agents/anthropic.svg",
      },
      {
        name: "Claude Code",
        href: "/ai-agents/interfaces/mcp/",
        icon: "/img/ai-agents/anthropic.svg",
      },
      {
        name: "ChatGPT",
        href: "/ai-agents/interfaces/mcp/",
        icon: "/img/ai-agents/openai.svg",
      },
      {
        name: "Codex",
        href: "/ai-agents/interfaces/mcp/",
        icon: "/img/ai-agents/openai.svg",
      },
      {
        name: "Cursor",
        href: "/ai-agents/interfaces/mcp/",
        icon: "/img/ai-agents/cursor.svg",
      },
      {
        name: "VS Code",
        href: "/ai-agents/interfaces/mcp/",
        icon: "/img/ai-agents/visualstudiocode.svg",
      },
      {
        name: "Windsurf",
        href: "/ai-agents/interfaces/mcp/",
        icon: "/img/ai-agents/windsurf.svg",
      },
    ],
  },
  {
    id: "sdk",
    label: "Python SDK",
    command: "uv add airbyte-agent-sdk",
    description: "Add the SDK to your Python project.",
    toolsLabel: "Or try one of our developer quickstarts.",
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
    skills: [
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
    ],
  },
  {
    id: "api",
    label: "API",
    command: null,
    description: "Integrate with the Agent API.",
    tools: [
      {
        name: "API reference",
        href: "/ai-agents/interfaces/api/",
        icon: "/img/favicon.png",
      },
    ],
  },
  {
    id: "webapp",
    label: "Web app",
    command: null,
    description:
      "Chat with an AI agent and build automations in your web browser. No code, nothing to install.",
    tools: [],
  },
];

export const QuickInstall = () => {
  const [activeTab, setActiveTab] = useState("mcp");
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
        <p className={styles.quickInstallDescription}>{tab.description}</p>
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
        {tab.id === "webapp" && (
          <div className={styles.toolChips}>
            <a className={styles.toolChip} href="https://app.airbyte.ai">
              <img
                className={styles.toolChipIcon}
                src="/img/favicon.png"
                alt="Airbyte"
              />
              <span>Open web app</span>
            </a>
          </div>
        )}
        {tab.toolsLabel && (
          <p className={styles.toolsLabel}>{tab.toolsLabel}</p>
        )}
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
        {tab.skills && tab.skills.length > 0 && (
          <div className={styles.skillsSection}>
            <p className={styles.skillsLabel}>
              Or have your agent build it for you.
            </p>
            <div className={styles.skillsChips}>
              {tab.skills.map((skill) => (
                <a
                  key={skill.name}
                  className={styles.skillChip}
                  href={skill.href}
                >
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
        )}
      </div>
    </div>
  );
};
