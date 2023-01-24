import classNames from "classnames";
import React from "react";

import { isCloudApp } from "utils/app";

import styles from "./MainPageWithScroll.module.scss";

/**
 * @param headTitle the title shown in the browser toolbar
 * @param pageTitle the title shown on the page
 */
interface MainPageWithScrollProps {
  headTitle?: React.ReactNode;
  pageTitle?: React.ReactNode;
  children?: React.ReactNode;
  noBottomPadding?: boolean;
}

export const MainPageWithScroll: React.FC<MainPageWithScrollProps> = ({
  headTitle,
  pageTitle,
  noBottomPadding,
  children,
}) => {
  return (
    <div className={styles.page}>
      <div>
        {headTitle}
        {pageTitle}
      </div>
      <div className={styles.contentContainer}>
        <div
          className={classNames(styles.content, {
            [styles.cloud]: isCloudApp(),
            [styles.noBottomPadding]: noBottomPadding,
          })}
        >
          {children}
        </div>
      </div>
    </div>
  );
};
