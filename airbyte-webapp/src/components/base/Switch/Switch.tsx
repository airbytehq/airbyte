import classnames from "classnames";
import React from "react";

import styles from "./Switch.module.scss";

interface SwitchProps extends React.InputHTMLAttributes<HTMLInputElement> {
  small?: boolean;
  loading?: boolean;
}

export const Switch: React.FC<SwitchProps> = ({ loading, small, checked, value, ...props }) => {
  const labelStyle = classnames(styles.switch, {
    [styles.small]: small,
    [styles.loading]: loading,
  });
  const spanStyle = classnames(styles.slider, {
    [styles.small]: small,
    [styles.loading]: loading,
  });

  return (
    // eslint-disable-next-line jsx-a11y/no-noninteractive-element-interactions
    <label
      className={labelStyle}
      onClick={(event: React.SyntheticEvent) => event.stopPropagation()}
      onKeyPress={(event: React.SyntheticEvent) => event.stopPropagation()}
    >
      <input
        {...props}
        className={styles.switchInput}
        type="checkbox"
        value={value}
        disabled={loading || props.disabled}
        checked={checked || !!value}
      />
      <span className={spanStyle} />
    </label>
  );
};
