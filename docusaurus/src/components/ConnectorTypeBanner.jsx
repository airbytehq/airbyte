import styles from "./ConnectorTypeBanner.module.css";

const ARROW_ICON = (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    height="0.75em"
    viewBox="0 0 512 512"
    style={{ verticalAlign: "middle" }}
  >
    <path
      fill="currentColor"
      d="M502.6 278.6c12.5-12.5 12.5-32.8 0-45.3l-128-128c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L402.7 224 32 224c-17.7 0-32 14.3-32 32s14.3 32 32 32l370.7 0-73.4 73.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0l128-128z"
    />
  </svg>
);

export const ConnectorTypeBanner = ({
  connectorType,
  counterpartUrl,
  connectorName,
}) => {
  const isAgent = connectorType === "agent";

  return (
    <div className={styles.banner}>
      <span className={styles.text}>
        {isAgent ? (
          <>
            This connector is optimized for AI agents. For the data replication
            connector, see{" "}
            <a href={counterpartUrl}>{connectorName}</a>. {ARROW_ICON}
          </>
        ) : (
          <>
            This connector is optimized for data replication, not AI agents. For
            agentic operations, see{" "}
            <a href={counterpartUrl}>{connectorName}</a>. {ARROW_ICON}
          </>
        )}
      </span>
    </div>
  );
};
