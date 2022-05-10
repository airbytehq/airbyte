import React from "react";

import styles from "./Switch.module.scss";

interface SwitchProps extends React.InputHTMLAttributes<HTMLInputElement> {
  small?: boolean;
  loading?: boolean;
}

const Switch: React.FC<SwitchProps> = ({ loading, small, checked, value, ...props }) => {
  const isChecked = checked || !!value;
  const labelStyle = `${styles.switch} ${small ? styles.small : ""} ${loading ? styles.loading : ""}`;
  const spanStyle = `${styles.slider} ${small ? styles.small : ""} ${isChecked ? styles.checked : ""}`;
  return (
    <label onClick={(event: React.SyntheticEvent) => event.stopPropagation()} className={labelStyle}>
      <input className={styles.switchInput} type="checkbox" {...props} value={value} checked={isChecked} />
      <span className={spanStyle} />
    </label>
  );
};

export default Switch;
