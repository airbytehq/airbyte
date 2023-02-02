import React, { PropsWithChildren } from "react";

import { FlexContainer } from "components/ui/Flex";

// eslint-disable-next-line css-modules/no-unused-class
import styles from "./SideBar.module.scss";

export const GenericSideBar: React.FC<PropsWithChildren<unknown>> = ({ children }) => {
  return (
    <nav className={styles.nav}>
      <FlexContainer
        direction="column"
        alignItems="center"
        justifyContent="space-between"
        className={styles.menuContent}
        gap="xs"
      >
        {children}
      </FlexContainer>
    </nav>
  );
};
