import styles from "./AgentConnectorTitle.module.css";

export const AgentConnectorTitle = ({ iconUrl, originalTitle }) => (
  <div className={styles.header}>
    <img
      src={iconUrl}
      alt=""
      className={styles.connectorIcon}
      onError={(e) => {
        e.target.style.display = "none";
      }}
    />
    <h1>{originalTitle}</h1>
  </div>
);
