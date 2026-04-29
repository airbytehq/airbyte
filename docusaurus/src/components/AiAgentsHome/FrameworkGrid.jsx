import React from "react";
import styles from "./AiAgentsHome.module.css";

const FRAMEWORKS = [
  {
    name: "Claude",
    href: "/ai-agents/interfaces/mcp/",
    icon: "https://cdn.simpleicons.org/anthropic/181818/ffffff",
  },
  {
    name: "Cursor",
    href: "/ai-agents/interfaces/mcp/",
    icon: "https://cdn.simpleicons.org/cursor/181818/ffffff",
  },
  {
    name: "ChatGPT",
    href: "/ai-agents/interfaces/mcp/",
    icon: "https://cdn.simpleicons.org/openai/181818/ffffff",
  },
  {
    name: "Pydantic AI",
    href: "/ai-agents/get-started/developer-quickstart/tutorial-pydantic",
    icon: "https://cdn.simpleicons.org/pydantic/181818/ffffff",
  },
  {
    name: "LangChain",
    href: "/ai-agents/get-started/developer-quickstart/tutorial-langchain",
    icon: "https://cdn.simpleicons.org/langchain/181818/ffffff",
  },
  {
    name: "FastMCP",
    href: "/ai-agents/get-started/developer-quickstart/tutorial-fastmcp",
    icon: "https://cdn.simpleicons.org/python/181818/ffffff",
  },
  {
    name: "HTTP API",
    href: "/ai-agents/interfaces/api/",
    icon: "https://cdn.simpleicons.org/fastapi/181818/ffffff",
  },
  {
    name: "VS Code",
    href: "/ai-agents/interfaces/mcp/",
    icon: "https://cdn.simpleicons.org/visualstudiocode/181818/ffffff",
  },
];

export const FrameworkGrid = () => {
  return (
    <div className={styles.frameworkSection}>
      <h2 className={styles.sectionHeading}>Works with your stack</h2>
      <p className={styles.sectionSubheading}>
        Connect any MCP-capable agent or build with the Python SDK.
      </p>
      <div className={styles.frameworkGrid}>
        {FRAMEWORKS.map((fw) => (
          <a key={fw.name} className={styles.frameworkCard} href={fw.href}>
            <img
              className={styles.frameworkIcon}
              src={fw.icon}
              alt={fw.name}
              loading="lazy"
            />
            <span className={styles.frameworkName}>{fw.name}</span>
          </a>
        ))}
      </div>
    </div>
  );
};
