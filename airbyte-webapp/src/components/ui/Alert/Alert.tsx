import classNames from "classnames";
import React, { PropsWithChildren } from "react";

import styles from "./Alert.module.scss";

interface AlertProps {
  variant: "yellow" | "blue";
}

export const Alert: React.FC<PropsWithChildren<AlertProps>> = ({ variant, children }) => {
  const containerStyles = classNames(styles.container, {
    [styles.yellow]: variant === "yellow",
    [styles.blue]: variant === "blue",
  });
  return <div className={containerStyles}>{children}</div>;
};
