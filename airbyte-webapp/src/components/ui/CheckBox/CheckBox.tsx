import { faCheck, faMinus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React, { InputHTMLAttributes } from "react";

import styles from "./CheckBox.module.scss";

export interface CheckBoxProps extends InputHTMLAttributes<HTMLInputElement> {
  indeterminate?: boolean;
  small?: boolean;
}

export const CheckBox: React.FC<CheckBoxProps> = ({ indeterminate, small, ...inputProps }) => {
  const { checked, disabled, className } = inputProps;
  const iconSize = small ? "sm" : "lg";

  return (
    <label
      className={classNames(
        styles.container,
        {
          [styles.checked]: checked,
          [styles.indeterminate]: indeterminate,
          [styles.disabled]: disabled,
          [styles.small]: small,
        },
        className
      )}
    >
      <input type="checkbox" aria-checked={checked} {...inputProps} />
      {indeterminate ? (
        <FontAwesomeIcon size={iconSize} icon={faMinus} />
      ) : (
        checked && <FontAwesomeIcon size={iconSize} icon={faCheck} />
      )}
    </label>
  );
};
