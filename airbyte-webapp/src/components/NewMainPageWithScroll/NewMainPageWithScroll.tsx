import classNames from "classnames";
import React from "react";

import styles from "./NewMainPageWithScroll.module.scss";

/**
 * @param headTitle the title shown in the browser toolbar
 * @param pageTitle the title shown on the page
 */
interface NewMainPageWithScrollProps {
  headTitle?: React.ReactNode;
  pageTitle?: React.ReactNode;
  children?: React.ReactNode;
  withPadding?: boolean;
}

const NewMainPageWithScroll: React.FC<NewMainPageWithScrollProps> = ({
  headTitle,
  pageTitle,
  withPadding,
  children,
}) => {
  return (
    <div className={styles.page}>
      <div>
        {headTitle}
        {pageTitle}
      </div>
      <div className={styles.contentContainer}>
        <div className={classNames(styles.content, { [styles.withPadding]: withPadding })}>{children}</div>
      </div>
    </div>
  );
};

export default NewMainPageWithScroll;
