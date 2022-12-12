import { faCheck, faMinus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React, { InputHTMLAttributes } from "react";

import styles from "./CheckBox.module.scss";

type CheckBoxSize = "lg" | "sm";

export interface CheckBoxProps extends InputHTMLAttributes<HTMLInputElement> {
  indeterminate?: boolean;
  elSize?: CheckBoxSize;
}

export const CheckBox: React.FC<CheckBoxProps> = ({ indeterminate, elSize = "lg", ...inputProps }) => {
  const { checked, disabled, className } = inputProps;

  return (
    <label
      className={classNames(
        styles.container,
        {
          [styles.checked]: checked,
          [styles.indeterminate]: indeterminate,
          [styles.disabled]: disabled,
          [styles.sizeLg]: elSize === "lg",
          [styles.sizeSm]: elSize === "sm",
        },
        className
      )}
    >
      <input type="checkbox" aria-checked={checked} {...inputProps} />
      {indeterminate ? (
        <FontAwesomeIcon size={elSize} icon={faMinus} />
      ) : (
        checked && <FontAwesomeIcon size={elSize} icon={faCheck} />
      )}
    </label>
  );
};
