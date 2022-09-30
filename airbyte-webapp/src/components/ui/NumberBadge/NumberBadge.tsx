import classnames from "classnames";
import React from "react";

import styles from "./NumberBadge.module.scss";

interface NumberBadgeProps {
  img?: string;
  num?: number;
  small?: boolean;
  color?: string;
  light?: boolean;
  ariaLabel?: string;
}

export const NumberBadge: React.FC<NumberBadgeProps> = ({ num, small, color, light, ariaLabel }) => {
  const imageCircleClassnames = classnames({
    [styles.circle]: num,
    [styles.small]: small && !num,
    [styles.darkBlue]: !small && num && !color,
    [styles.green]: color === "green",
    [styles.red]: color === "red",
    [styles.blue]: color === "blue",
    [styles.light]: light,
  });

  const numberStyles = classnames(styles.number, { [styles.light]: light });

  return (
    <div className={imageCircleClassnames} aria-label={ariaLabel}>
      <div className={numberStyles}>{num}</div>
    </div>
  );
};
