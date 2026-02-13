import styles from "./AgentConnectorRegistry.module.css";

const ICON_BASE_URL =
  "https://connectors.airbyte.com/files/metadata/airbyte";
const CHANGELOG_BASE_URL =
  "https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors";

const iconStyle = { maxWidth: 25, maxHeight: 25 };

function formatConnectorName(slug) {
  return slug
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export default function AgentConnectorRegistry({ connectors: connectorJson }) {
  const connectors = JSON.parse(connectorJson)
    .map((slug) => ({
      slug,
      name: formatConnectorName(slug),
      href: `/ai-agents/connectors/${slug}/`,
      iconUrl: `${ICON_BASE_URL}/source-${slug}/latest/icon.svg`,
    }))
    .sort((a, b) => a.name.localeCompare(b.name));

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
                    onError={(e) => {
                      e.target.style.display = "none";
                    }}
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
