import classNames from "classnames";
import React from "react";

import { H5 } from "../Titles";
import styles from "./Card.module.scss";

export interface CardProps {
  title?: React.ReactNode;
  className?: string;
  fullWidth?: boolean;
  lightPadding?: boolean;
  withPadding?: boolean;
  roundedBottom?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  title,
  className,
  fullWidth,
  lightPadding,
  withPadding,
  roundedBottom,
}) => {
  return (
    <div
      className={classNames(
        className,
        styles.container,
        fullWidth ? styles.fullWidth : undefined,
        withPadding ? styles.withPadding : undefined
      )}
    >
      {title ? (
        <H5
          className={classNames(
            styles.title,
            lightPadding || !children ? styles.lightPadding : undefined,
            roundedBottom ? styles.roundedBottom : undefined
          )}
        >
          {title}
        </H5>
      ) : null}
      {children}
    </div>
  );
};
