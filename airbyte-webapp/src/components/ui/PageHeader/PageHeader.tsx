import classNames from "classnames";
import React from "react";

import { Text } from "components/ui/Text";

import styles from "./PageHeader.module.scss";

interface PageHeaderProps {
  withLine?: boolean;
  middleComponent?: React.ReactNode;
  middleTitleBlock?: React.ReactNode;
  endComponent?: React.ReactNode;
  title: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  withLine,
  middleComponent,
  middleTitleBlock,
  endComponent,
}) => (
  <div className={classNames(styles.container)} data-withline={withLine}>
    <Text
      as="h1"
      size="md"
      className={classNames(styles.start, {
        [styles.withLine]: withLine,
      })}
    >
      {title}
    </Text>
    {middleTitleBlock ? (
      <Text
        as="h3"
        size="md"
        className={classNames(styles.heading, {
          [styles.middle]: middleTitleBlock,
        })}
      >
        {middleTitleBlock}
      </Text>
    ) : (
      <div className={classNames(styles.middle)}>{middleComponent}</div>
    )}
    <div className={classNames(styles.end)}>{endComponent}</div>
  </div>
);
