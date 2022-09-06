import { ReleaseStageBadge } from "components/ReleaseStageBadge";

import { ReleaseStage } from "core/request/AirbyteClient";
import { getIcon } from "utils/imageUtils";

import styles from "./ConnectorCard.module.scss";

export interface ConnectorCardProps {
  connectionName: string;
  icon?: string;
  connectorName: string;
  releaseStage?: ReleaseStage;
}

const ConnectorCard = (props: ConnectorCardProps) => {
  const { connectionName, connectorName, icon, releaseStage } = props;

  return (
    <div className={styles.container}>
      {icon && <div className={styles.entityIcon}>{getIcon(icon)}</div>}
      <div className={styles.details}>
        <div className={styles.connectorDetails}>
          <div className={styles.connectionName}>{connectionName}</div>
          {releaseStage && <ReleaseStageBadge stage={releaseStage} />}
        </div>
        <div className={styles.connectorName}>{connectorName} </div>
      </div>
    </div>
  );
};

export default ConnectorCard;
