import classnames from "classnames";
import React from "react";

import styles from "./MainPageWithScroll.module.scss";

/**
 * @param headTitle the title shown in the browser toolbar
 * @param pageTitle the title shown on the page
 */
interface MainPageWithScrollProps {
  error?: React.ReactNode;
  headTitle?: React.ReactNode;
  pageTitle?: React.ReactNode;
  children?: React.ReactNode;
}

const MainPageWithScroll: React.FC<MainPageWithScrollProps> = ({ error, headTitle, pageTitle, children }) => {
  return (
    <div className={styles.page}>
      {error}
      <div className={classnames({ [styles.headerError]: !!error })}>
        {headTitle}
        {pageTitle}
      </div>
      <div className={styles.content}>{children}</div>
    </div>
  );
};

export default MainPageWithScroll;
