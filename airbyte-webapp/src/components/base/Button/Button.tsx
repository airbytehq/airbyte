import { faCircleNotch } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";

import styles from "./Button.module.scss";
import { ButtonProps, ButtonType } from "./types";

export const Button: React.FC<ButtonProps> = (props) => {
  const classNamesObject = {
    [styles.full]: props.full,
    [styles.size_l]: props.size === "l",
    [styles.size_s]: props.size === "s",
    [styles.size_xs]: props.size === "xs",
    [styles.type_danger]: props.buttonType === ButtonType.Danger,
    [styles.type_light_grey]: props.buttonType === ButtonType.LightGrey,
    [styles.type_primary]: props.buttonType === ButtonType.Primary,
    [styles.type_secondary]: props.buttonType === ButtonType.Secondary,
  };
  const widthStyle: { width?: string } = {};
  if (props.width) {
    widthStyle.width = `${props.width}px`;
  }
  return (
    <button
      style={widthStyle}
      className={classNames(styles.button, props.customStyles, {
        [styles.is_loading]: props.isLoading,
        ...classNamesObject,
      })}
      {...props}
    >
      {props.isLoading && (
        <FontAwesomeIcon
          className={classNames(styles.button_icon, {
            [styles.is_spinner_icon]: true,
            ...classNamesObject,
          })}
          icon={faCircleNotch}
        />
      )}
      {props.icon &&
        props.iconPosition === "left" &&
        React.cloneElement(props.icon, {
          className: classNames(styles.button_icon, {
            [styles.is_loading]: props.isLoading,
            [styles.position_left]: true,
            [styles.is_regular_icon]: true,
            [styles.with_label]: Boolean(props.label),
            ...classNamesObject,
          }),
        })}
      {props.label}
      {props.icon &&
        props.iconPosition === "right" &&
        React.cloneElement(props.icon, {
          className: classNames(styles.button_icon, {
            [styles.is_loading]: props.isLoading,
            [styles.position_right]: true,
            [styles.is_regular_icon]: true,
            [styles.with_label]: Boolean(props.label),
            ...classNamesObject,
          }),
        })}
    </button>
  );
};

Button.defaultProps = {
  full: false,
  size: "s",
  buttonType: ButtonType.Primary,
  iconPosition: "left",
};
