import classNames from "classnames";
import React, { PropsWithChildren } from "react";
import { useLocation } from "react-router-dom";

import { FlexContainer } from "components/ui/Flex";

// eslint-disable-next-line css-modules/no-unused-class
import styles from "./SideBar.module.scss";

export const useCalculateSidebarStyles = () => {
  const location = useLocation();

  const menuItemStyle = (isActive: boolean) => {
    const isChild = location.pathname.split("/").length > 4 && location.pathname.split("/")[3] !== "settings";
    return classNames(styles.menuItem, { [styles.active]: isActive, [styles.activeChild]: isChild && isActive });
  };

  return ({ isActive }: { isActive: boolean }) => menuItemStyle(isActive);
};

export const GenericSideBar: React.FC<PropsWithChildren<unknown>> = ({ children }) => {
  // const config = useConfig();
  // const navLinkClassName = useCalculateSidebarStyles();
  // const { formatMessage } = useIntl();

  // const bottomMenuArray = bottomMenuItems ?? OSSBottomMenuItems;

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
        {/* <FlexItem />
        <FlexContainer
          direction="column"
          alignItems="center"
          justifyContent="space-between"
          className={styles.menuContent}
        >
          <TopItems />
          <FlexItem className={styles.menuContent}>
            <MainNav />
          </FlexItem>
          <ul className={styles.menu} data-testid="navBottomMenu">
            <FlexItem className={styles.bottomMenu}>
              <FlexContainer direction="column" gap="xs">
                {bottomMenuArray.map((item, idx) => {
                  // todo: better key
                  return <li key={idx}>{item}</li>;
                })}
              </FlexContainer>
            </FlexItem>
          </ul>
        </FlexContainer> */}
      </FlexContainer>
    </nav>
  );
};
