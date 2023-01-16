import React from "react";
import { FormattedMessage } from "react-intl";

import { getIcon } from "utils/imageUtils";

import styles from "./ConnectorHeaderGroupIcon.module.scss";

interface StreamHeaderGroupIconProps {
  type: "source" | "destination";
  icon?: string;
}

export const ConnectorHeaderGroupIcon: React.FC<StreamHeaderGroupIconProps> = ({ type, icon }) => {
  return (
    <span className={styles.connectorIconContainer}>
      <div className={styles.icon}>{getIcon(icon)}</div>
      <FormattedMessage id={`connector.${type}`} />
    </span>
  );
};
