import classnames from "classnames";
import React from "react";

import styles from "./NumberBadge.module.scss";

interface NumberBadgeProps {
  value: number;
  color?: "green" | "red" | "blue" | "default";
  className?: string;
  "aria-label"?: string;
}

export const NumberBadge: React.FC<NumberBadgeProps> = ({ value, color, className, "aria-label": ariaLabel }) => {
  const numberBadgeClassnames = classnames(styles.circle, className, {
    [styles.default]: !color || color === "default",
    [styles.green]: color === "green",
    [styles.red]: color === "red",
    [styles.blue]: color === "blue",
  });

  return (
    <div className={numberBadgeClassnames} aria-label={ariaLabel}>
      {value}
    </div>
  );
};
