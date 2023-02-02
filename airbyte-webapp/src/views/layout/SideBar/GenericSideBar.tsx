import React, { PropsWithChildren } from "react";

import { MenuContent } from "./components/MenuContent";
import styles from "./SideBar.module.scss";

export const GenericSideBar: React.FC<PropsWithChildren<unknown>> = ({ children }) => {
  return (
    <nav className={styles.nav}>
      <MenuContent>{children}</MenuContent>
    </nav>
  );
};
