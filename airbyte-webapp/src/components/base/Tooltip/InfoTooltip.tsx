import React from "react";

import { InfoIcon } from "components/icons/InfoIcon";

import styles from "./InfoTooltip.module.scss";
import { Tooltip } from "./Tooltip";

export const InfoTooltip: React.FC = ({ children }) => {
  return (
    <Tooltip
      control={
        <div className={styles.container}>
          <div className={styles.icon}>
            <InfoIcon />
          </div>
        </div>
      }
    >
      {children}
    </Tooltip>
  );
};
