import classnames from "classnames";
import React from "react";

import styles from "./Switch.module.scss";

interface SwitchProps extends React.InputHTMLAttributes<HTMLInputElement> {
  small?: boolean;
  loading?: boolean;
  swithSize?: string;
}

export const Switch: React.FC<SwitchProps> = ({ loading, swithSize, small, checked, value, ...props }) => {
  const labelStyle = classnames(styles.switch, {
    [styles.small]: small || swithSize === "small",
    [styles.medium]: swithSize === "medium",
    [styles.loading]: loading,
  });
  const spanStyle = classnames(styles.slider, {
    [styles.small]: small || swithSize === "small",
    [styles.medium]: swithSize === "medium",
    [styles.loading]: loading,
  });

  return (
    <label className={labelStyle}>
      <input
        {...props}
        className={styles.switchInput}
        type="checkbox"
        value={value}
        disabled={loading || props.disabled}
        defaultChecked={checked || !!value}
      />
      <span className={spanStyle} />
    </label>
  );
};
