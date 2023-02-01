import classNames from "classnames";
import React from "react";

import { H5 } from "components/base/Titles";
import { Text } from "components/ui/Text";

import styles from "./Card.module.scss";
import { InfoTooltip } from "../Tooltip";

export interface CardProps {
  title?: React.ReactNode;
  description?: React.ReactNode;
  className?: string;
  fullWidth?: boolean;
  lightPadding?: boolean;
  withPadding?: boolean;
  roundedBottom?: boolean;
}

export const Card: React.FC<React.PropsWithChildren<CardProps>> = ({
  children,
  title,
  description,
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
        <div
          className={classNames(styles.header, {
            [styles.lightPadding]: lightPadding || !children,
            [styles.roundedBottom]: roundedBottom,
            [styles.withDescription]: description,
          })}
        >
          <H5 className={classNames(styles.title)}>{title}</H5>
          {description && (
            <InfoTooltip>
              <Text className={styles.infoTooltip} size="sm">
                {description}
              </Text>
            </InfoTooltip>
          )}
        </div>
      ) : null}
      {children}
    </div>
  );
};
