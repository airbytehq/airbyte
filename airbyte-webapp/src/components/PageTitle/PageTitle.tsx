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
  <div className={classNames(styles.mainContainer, { [styles.withLine]: withLine })}>
    <H3 className={styles.titleBlock}>{title}</H3>
    {middleTitleBlock ? (
      <div className={styles.middleTitleBlock}>{middleTitleBlock}</div>
    ) : (
      <div className={styles.middleBlock}>{middleComponent}</div>
    )}
    <div className={styles.endBlock}>{endComponent}</div>
  </div>
);

export default PageTitle;
