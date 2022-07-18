import classNames from "classnames";
import React from "react";

import styles from "./ToolTip.module.scss";

interface ToolTipProps {
  control: React.ReactNode;
  className?: string;
  disabled?: boolean;
  cursor?: "pointer" | "help" | "not-allowed";
}

export const ToolTip: React.FC<ToolTipProps> = ({ children, control, className, disabled, cursor }) => (
  <div className={styles.container} style={disabled ? undefined : { cursor }}>
    {control}
    <div className={classNames(styles.toolTip, className, { disabled })}>{children}</div>
  </div>
);
