import classNames from "classnames";
import React from "react";

import { H3 } from "components";

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
    <H3
      className={classNames(styles.titleBlock, {
        [styles.withLine]: withLine,
      })}
    >
      {title}
    </H3>
    {middleTitleBlock ? (
      <H3 className={classNames(styles.middleTitleBlock)}>{middleTitleBlock}</H3>
    ) : (
      <div className={classNames(styles.middleBlock)}>{middleComponent}</div>
    )}
    <div className={classNames(styles.endBlock)}>{endComponent}</div>
  </div>
);

export default PageTitle;
