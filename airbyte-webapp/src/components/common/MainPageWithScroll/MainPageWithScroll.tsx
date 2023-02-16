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
  softScrollEdge?: boolean;
}

export const MainPageWithScroll: React.FC<MainPageWithScrollProps> = ({
  headTitle,
  pageTitle,
  noBottomPadding,
  softScrollEdge = true,
  children,
}) => {
  return (
    <>
      {headTitle}
      <div className={styles.container}>
        {pageTitle && <div>{pageTitle}</div>}
        <div
          className={classNames(styles.contentContainer, {
            [styles.softScrollEdge]: softScrollEdge,
          })}
        >
          <div className={styles.contentScroll}>
            {softScrollEdge && <div className={styles.edge} aria-hidden="true" />}
            <div
              className={classNames(styles.content, {
                [styles.noBottomPadding]: noBottomPadding,
                [styles.cloud]: isCloudApp(),
              })}
            >
              {children}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
