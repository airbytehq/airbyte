import React from "react";

import styles from "./MainPageWithScroll.module.scss";

/**
 * @param headTitle the title shown in the browser toolbar
 * @param pageTitle the title shown on the page
 */
interface MainPageWithScrollProps {
  headTitle?: React.ReactNode;
  pageTitle?: React.ReactNode;
  children?: React.ReactNode;
}

const MainPageWithScroll: React.FC<MainPageWithScrollProps> = ({ headTitle, pageTitle, children }) => {
  return (
    <div className={styles.page}>
      <div>
        {headTitle}
        {pageTitle}
      </div>
      <div className={styles.contentContainer}>
        <div className={styles.content}>{children}</div>
      </div>
    </div>
  );
};

export default MainPageWithScroll;
