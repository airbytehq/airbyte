import { faCheck, faMinus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";

import styles from "./CheckBox.module.scss";

export const CheckBox: React.FC<React.InputHTMLAttributes<HTMLInputElement> & { indeterminate?: boolean }> = ({
  indeterminate,
  className,
  checked,
  ...rest
}) => (
  <label
    className={classNames(
      styles.label,
      { [styles["label--indeterminate"]]: indeterminate, [styles["label--checked"]]: checked },
      className
    )}
  >
    <input {...rest} checked={checked} type="checkbox" className={styles.input} />
    {indeterminate ? <FontAwesomeIcon icon={faMinus} /> : checked && <FontAwesomeIcon icon={faCheck} />}
  </label>
);
