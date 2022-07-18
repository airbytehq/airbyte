import classNames from "classnames";
import React from "react";

import styles from "./ToolTip.module.scss";

interface ToolTipProps {
  control: React.ReactNode;
  className?: string;
  disabled?: boolean;
  cursor?: "pointer" | "help" | "not-allowed" | "initial";
  mode?: "dark" | "light";
}

export const ToolTip: React.FC<ToolTipProps> = ({ children, control, className, disabled, mode = "dark", cursor }) => (
  <div className={styles.container} style={disabled ? undefined : { cursor }}>
    {control}
    <div
      className={classNames(styles.toolTip, mode === "light" && styles.light, disabled && styles.disabled, className)}
    >
      {children}
    </div>
  </div>
);
