import { faRightLeft, faRobot } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import styles from "./ConnectorTypeBanner.module.css";

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
            <FontAwesomeIcon icon={faRobot} className={styles.icon} /> This
            connector is optimized for AI agents. For the data replication
            connector, see <a href={counterpartUrl}>{connectorName}</a>.
          </>
        ) : (
          <>
            <FontAwesomeIcon icon={faRightLeft} className={styles.icon} /> This
            connector is optimized for data replication, not AI agents. For
            agentic operations, see{" "}
            <a href={counterpartUrl}>{connectorName}</a>.
          </>
        )}
      </span>
    </div>
  );
};
