import styles from "./AgentConnectorTitle.module.css";

export const AgentConnectorTitle = ({ iconUrl, originalTitle }) => (
  <div className={styles.header}>
    <img src={iconUrl} alt="" className={styles.connectorIcon} />
    <h1>{originalTitle}</h1>
  </div>
);
