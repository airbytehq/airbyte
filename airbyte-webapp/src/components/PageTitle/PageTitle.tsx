import classNames from "classnames";
import React from "react";

import { Text } from "components/base/Text";

import styles from "./PageTitle.module.scss";

interface PageTitleProps {
  withLine?: boolean;
  middleComponent?: React.ReactNode;
  middleTitleBlock?: React.ReactNode;
  endComponent?: React.ReactNode;
  title: React.ReactNode;
}

const PageTitle: React.FC<PageTitleProps> = ({ title, withLine, middleComponent, middleTitleBlock, endComponent }) => (
  <div className={classNames(styles.container)} data-withLine={withLine}>
    <Text
      as="h3"
      size="md"
      className={classNames(styles.titleBlock, {
        [styles.withLine]: withLine,
      })}
    >
      {title}
    </Text>
    {middleTitleBlock ? (
      <Text as="h3" size="md" className={classNames(styles.middleTitleBlock)}>
        {middleTitleBlock}
      </Text>
    ) : (
      <div className={classNames(styles.middleBlock)}>{middleComponent}</div>
    )}
    <div className={classNames(styles.endBlock)}>{endComponent}</div>
  </div>
);

export default PageTitle;
