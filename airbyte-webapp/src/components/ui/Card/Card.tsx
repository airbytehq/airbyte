import classNames from "classnames";
import React from "react";

import { H5 } from "components/base/Titles";

import styles from "./Card.module.scss";

export interface CardProps {
  title?: React.ReactNode;
  className?: string;
  fullWidth?: boolean;
  lightPadding?: boolean;
  withPadding?: boolean;
  roundedBottom?: boolean;
}

export const Card: React.FC<React.PropsWithChildren<CardProps>> = ({
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
      className={classNames(className, styles.container, {
        [styles.fullWidth]: fullWidth,
        [styles.withPadding]: withPadding,
      })}
    >
      {title ? (
        <H5
          className={classNames(styles.title, {
            [styles.lightPadding]: lightPadding || !children,
            [styles.roundedBottom]: roundedBottom,
          })}
        >
          {title}
        </H5>
      ) : null}
      {children}
    </div>
  );
};
