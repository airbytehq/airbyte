import classNames from "classnames";
import React, { PropsWithChildren } from "react";

import styles from "./Alert.module.scss";

interface AlertProps {
  variant: "yellow" | "blue";
  className?: string;
}

export const Alert: React.FC<PropsWithChildren<AlertProps>> = ({ variant = "blue", children, className }) => {
  const containerStyles = classNames(styles.container, className, {
    [styles.yellow]: variant === "yellow",
    [styles.blue]: variant === "blue",
  });
  return <div className={containerStyles}>{children}</div>;
};
