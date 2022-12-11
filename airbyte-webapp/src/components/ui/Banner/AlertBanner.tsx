import classnames from "classnames";
import React from "react";

import styles from "./AlertBanner.module.scss";

interface AlertBannerProps {
  color?: "default" | "warning";
  message: React.ReactNode;
}

export const AlertBanner: React.FC<AlertBannerProps> = ({ color, message }) => {
  const bannerStyle = classnames(styles.alertBannerContainer, {
    [styles.default]: color === "default" || !color,
    [styles.red]: color === "warning",
  });

  return <div className={bannerStyle}>{message}</div>;
};
