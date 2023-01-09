import classNames from "classnames";
import React from "react";

import { Heading } from "components/ui/Heading";

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
    <Heading
      as="h1"
      className={classNames(styles.start, {
        [styles.withLine]: withLine,
      })}
    >
      {title}
    </Heading>
    {middleTitleBlock ? (
      <Heading
        as="h3"
        className={classNames(styles.heading, {
          [styles.middle]: middleTitleBlock,
        })}
      >
        {middleTitleBlock}
      </Heading>
    ) : (
      <div className={classNames(styles.middle)}>{middleComponent}</div>
    )}
    <div className={classNames(styles.end)}>{endComponent}</div>
  </div>
);
