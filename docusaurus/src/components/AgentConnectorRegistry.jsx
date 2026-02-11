import { useDocsSidebar } from "@docusaurus/plugin-content-docs/client";
import styles from "./AgentConnectorRegistry.module.css";

const ICON_BASE_URL =
  "https://connectors.airbyte.com/files/metadata/airbyte";
const CHANGELOG_BASE_URL =
  "https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors";

const iconStyle = { maxWidth: 25, maxHeight: 25 };

function extractConnectorSlug(href) {
  const match = href.match(/connectors\/([^/]+)/);
  return match ? match[1] : null;
}

function formatConnectorName(slug) {
  return slug
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function getConnectorItems(sidebar) {
  if (!sidebar || !sidebar.items) return [];

  return sidebar.items
    .filter((item) => {
      const href = item.href || "";
      return (
        href.includes("/connectors/") &&
        href !== "/ai-agents/connectors/" &&
        !href.endsWith("/connectors")
      );
    })
    .map((item) => {
      const slug = extractConnectorSlug(item.href);
      if (!slug) return null;

      return {
        slug,
        name: formatConnectorName(slug),
        href: item.href,
        iconUrl: `${ICON_BASE_URL}/source-${slug}/latest/icon.svg`,
      };
    })
    .filter(Boolean)
    .sort((a, b) => a.name.localeCompare(b.name));
}

export default function AgentConnectorRegistry() {
  const sidebar = useDocsSidebar();
  const connectors = getConnectorItems(sidebar);

  if (connectors.length === 0) {
    return <div>Loading agent connectors...</div>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Connector</th>
          <th style={{ textAlign: "center" }}>Links</th>
        </tr>
      </thead>
      <tbody>
        {connectors.map((connector) => (
          <tr key={connector.slug}>
            <td>
              <div className={styles.connectorName}>
                <div className={styles.connectorIconBackground}>
                  <img
                    src={connector.iconUrl}
                    style={iconStyle}
                    alt=""
                    loading="lazy"
                  />
                </div>
                <a href={connector.href}>{connector.name}</a>
              </div>
            </td>
            <td>
              <div className={styles.links}>
                <a href={connector.href} title="Overview">
                  Overview
                </a>
                <span className={styles.linkSeparator}>|</span>
                <a href={`${connector.href}AUTH`} title="Authentication">
                  Auth
                </a>
                <span className={styles.linkSeparator}>|</span>
                <a href={`${connector.href}REFERENCE`} title="API Reference">
                  Reference
                </a>
                <span className={styles.linkSeparator}>|</span>
                <a
                  href={`${CHANGELOG_BASE_URL}/${connector.slug}/CHANGELOG.md`}
                  title="Changelog"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Changelog
                </a>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
