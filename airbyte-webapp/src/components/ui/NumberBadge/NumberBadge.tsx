import classnames from "classnames";
import React from "react";

import styles from "./NumberBadge.module.scss";

interface NumberBadgeProps {
  value: number;
  color?: string;
  "aria-label"?: string;
}

export const NumberBadge: React.FC<NumberBadgeProps> = ({ value, color, "aria-label": ariaLabel }) => {
  const imageCircleClassnames = classnames(styles.circle, {
    [styles.darkBlue]: !color,
    [styles.green]: color === "green",
    [styles.red]: color === "red",
    [styles.blue]: color === "blue",
  });

  return (
    <div className={imageCircleClassnames} aria-label={ariaLabel}>
      <div className={styles.number}>{value}</div>
    </div>
  );
};
