import classnames from "classnames";
import React from "react";

import { ReleaseStageBadge } from "components/ReleaseStageBadge";

import { ReleaseStage } from "core/request/AirbyteClient";
import { getIcon } from "utils/imageUtils";

import styles from "./ConnectorCard.module.scss";

export interface ConnectorCardProps {
  connectionName: string;
  icon?: string;
  connectorName?: string;
  releaseStage?: ReleaseStage;
  fullWidth?: boolean;
}

export const ConnectorCard: React.FC<ConnectorCardProps> = ({
  connectionName,
  connectorName,
  icon,
  releaseStage,
  fullWidth,
}) => (
  <div className={classnames(styles.container, { [styles.fullWidth]: fullWidth })}>
    {icon && <div className={styles.entityIcon}>{getIcon(icon)}</div>}
    <div className={styles.details}>
      <div className={styles.connectorDetails}>
        <div className={styles.connectionName}>{connectionName}</div>
        {releaseStage && <ReleaseStageBadge stage={releaseStage} />}
      </div>
      {connectorName && <div className={styles.connectorName}>{connectorName} </div>}
    </div>
  </div>
);
