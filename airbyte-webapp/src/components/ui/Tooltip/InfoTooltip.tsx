import React from "react";

import { InfoIcon } from "components/icons/InfoIcon";

import styles from "./InfoTooltip.module.scss";
import { Tooltip } from "./Tooltip";
import { InfoTooltipProps } from "./types";

export const InfoTooltip: React.FC<React.PropsWithChildren<InfoTooltipProps>> = ({ children, ...props }) => {
  return (
    <Tooltip
      {...props}
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
