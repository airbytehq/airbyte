import classnames from "classnames";
import React from "react";

import styles from "./Switch.module.scss";

type SwitchSize = "lg" | "sm" | "xs";

type SwitchVariant = "default" | "strong-blue";

interface SwitchProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "size"> {
  indeterminate?: boolean;
  loading?: boolean;
  size?: SwitchSize;
  variant?: SwitchVariant;
}

export const Switch: React.FC<SwitchProps> = ({
  checked,
  disabled,
  indeterminate,
  loading,
  size = "lg",
  value,
  variant = "default",
  ...props
}) => {
  const labelStyle = classnames(styles.switch, {
    [styles.sizeLg]: size === "lg",
    [styles.sizeSm]: size === "sm",
    [styles.sizeXs]: size === "xs",
    [styles.loading]: loading,
  });
  const spanStyle = classnames(styles.slider, {
    [styles.sizeLg]: size === "lg",
    [styles.sizeSm]: size === "sm",
    [styles.sizeXs]: size === "xs",
    [styles.variantDefault]: variant === "default",
    [styles.variantStrongBlue]: variant === "strong-blue",
    [styles.indeterminate]: indeterminate,
    [styles.loading]: loading,
  });

  return (
    <label className={labelStyle}>
      <input
        {...props}
        aria-checked={(indeterminate ? "mixed" : checked) ?? !!value}
        className={styles.switchInput}
        type="checkbox"
        value={value}
        disabled={loading || disabled}
        checked={checked || !!value}
      />
      <span className={spanStyle} />
    </label>
  );
};
