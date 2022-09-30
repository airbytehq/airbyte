import { faCircleNotch } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";

import styles from "./Button.module.scss";
import { ButtonProps } from "./types";

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>((props, ref) => {
  const {
    children,
    className,
    clickable,
    full,
    icon,
    iconPosition,
    isLoading,
    size,
    variant,
    wasActive,
    width,
    ...buttonProps
  } = props;
  const buttonStyles = {
    [styles.full]: full,
    [styles.isLoading]: isLoading,
    [styles.sizeL]: size === "lg",
    [styles.sizeS]: size === "sm",
    [styles.sizeXS]: size === "xs",
    [styles.typeDanger]: variant === "danger",
    [styles.typeClear]: variant === "clear",
    [styles.typeLight]: variant === "light",
    [styles.typePrimary]: variant === "primary",
    [styles.typeSecondary]: variant === "secondary",
  };
  const widthStyle: { width?: string } = {};
  if (width) {
    widthStyle.width = `${width}px`;
  }
  return (
    <button
      ref={ref}
      style={widthStyle}
      className={classNames(styles.button, className, buttonStyles)}
      {...buttonProps}
    >
      {isLoading && (
        <FontAwesomeIcon
          className={classNames(styles.buttonIcon, {
            [styles.isSpinnerIcon]: true,
          })}
          icon={faCircleNotch}
        />
      )}
      {icon &&
        iconPosition === "left" &&
        React.cloneElement(icon, {
          className: classNames(styles.buttonIcon, {
            [styles.positionLeft]: true,
            [styles.isRegularIcon]: true,
            [styles.withLabel]: Boolean(children),
          }),
        })}
      <div className={styles.childrenContainer}>{children}</div>
      {icon &&
        iconPosition === "right" &&
        React.cloneElement(icon, {
          className: classNames(styles.buttonIcon, {
            [styles.positionRight]: true,
            [styles.isRegularIcon]: true,
            [styles.withLabel]: Boolean(children),
          }),
        })}
    </button>
  );
});

Button.defaultProps = {
  full: false,
  size: "xs",
  variant: "primary",
  iconPosition: "left",
};
