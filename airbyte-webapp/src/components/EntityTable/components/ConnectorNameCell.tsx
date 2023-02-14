import React from "react";

import { ConnectorIcon } from "components/common/ConnectorIcon";

import styles from "./ConnectorNameCell.module.scss";
import { EntityNameCell } from "./EntityNameCell";

interface ConnectorNameCellProps {
  enabled: boolean;
  value: string;
  icon: string | undefined;
}

export const ConnectorNameCell: React.FC<ConnectorNameCellProps> = ({ value, enabled, icon }) => {
  return (
    <div className={styles.content} title={value}>
      <ConnectorIcon icon={icon} />
      <EntityNameCell className={styles.text} value={value} enabled={enabled} />
    </div>
  );
};
