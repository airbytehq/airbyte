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
        <span className={styles.container}>
          <span className={styles.icon}>
            <InfoIcon />
          </span>
        </span>
      }
    >
      {children}
    </Tooltip>
  );
};
