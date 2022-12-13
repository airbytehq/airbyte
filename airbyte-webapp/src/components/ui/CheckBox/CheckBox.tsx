import { faCheck, faMinus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React, { InputHTMLAttributes } from "react";

import styles from "./CheckBox.module.scss";

type CheckBoxSize = "lg" | "sm";

export interface CheckBoxProps extends InputHTMLAttributes<HTMLInputElement> {
  indeterminate?: boolean;
  checkboxSize?: CheckBoxSize;
}

export const CheckBox: React.FC<CheckBoxProps> = ({ indeterminate, checkboxSize = "lg", ...inputProps }) => {
  const { checked, disabled, className } = inputProps;

  return (
    <label
      className={classNames(
        styles.container,
        {
          [styles.checked]: checked,
          [styles.indeterminate]: indeterminate,
          [styles.disabled]: disabled,
          [styles.sizeLg]: checkboxSize === "lg",
          [styles.sizeSm]: checkboxSize === "sm",
        },
        className
      )}
    >
      <input type="checkbox" aria-checked={indeterminate ? "mixed" : checked} {...inputProps} />
      {indeterminate ? (
        <FontAwesomeIcon size={checkboxSize} icon={faMinus} />
      ) : (
        checked && <FontAwesomeIcon size={checkboxSize} icon={faCheck} />
      )}
    </label>
  );
};
