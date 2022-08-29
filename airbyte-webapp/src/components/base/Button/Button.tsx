import { faCircleNotch } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";

import styles from "./Button.module.scss";
import { ButtonProps } from "./types";

export const Button: React.FC<ButtonProps> = (props) => {
  const buttonStyles = {
    [styles.full]: props.full,
    [styles.isLoading]: props.isLoading,
    [styles.sizeL]: props.size === "lg",
    [styles.sizeS]: props.size === "sm",
    [styles.sizeXS]: props.size === "xs",
    [styles.typeDanger]: props.variant === "danger",
    [styles.typeLight]: props.variant === "light",
    [styles.typePrimary]: props.variant === "primary",
    [styles.typeSecondary]: props.variant === "secondary",
  };
  const widthStyle: { width?: string } = {};
  if (props.width) {
    widthStyle.width = `${props.width}px`;
  }
  return (
    <button style={widthStyle} className={classNames(styles.button, props.customStyles, buttonStyles)} {...props}>
      {props.isLoading && (
        <FontAwesomeIcon
          className={classNames(styles.buttonIcon, {
            [styles.isSpinnerIcon]: true,
            ...buttonStyles,
          })}
          icon={faCircleNotch}
        />
      )}
      {props.icon &&
        props.iconPosition === "left" &&
        React.cloneElement(props.icon, {
          className: classNames(styles.buttonIcon, {
            [styles.positionLeft]: true,
            [styles.isRegularIcon]: true,
            [styles.withLabel]: Boolean(props.children),
            ...buttonStyles,
          }),
        })}
      {props.children}
      {props.icon &&
        props.iconPosition === "right" &&
        React.cloneElement(props.icon, {
          className: classNames(styles.buttonIcon, {
            [styles.positionRight]: true,
            [styles.isRegularIcon]: true,
            [styles.withLabel]: Boolean(props.children),
            ...buttonStyles,
          }),
        })}
    </button>
  );
};

Button.defaultProps = {
  full: false,
  size: "sm",
  variant: "primary",
  iconPosition: "left",
};
