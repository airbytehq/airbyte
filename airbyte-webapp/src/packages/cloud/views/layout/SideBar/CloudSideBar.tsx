import React from "react";

import { FlexContainer } from "components/ui/Flex";

import { AirbyteHomeLink } from "views/layout/SideBar/AirbyteHomeLink";
import { GenericSideBar } from "views/layout/SideBar/GenericSideBar";
import { MainNav } from "views/layout/SideBar/MainNav";

// eslint-disable-next-line css-modules/no-unused-class

import { CloudBottomItems } from "./CloudBottomItems";
import styles from "./CloudSideBar.module.scss";
import { WorkspacePopout } from "../../workspaces/WorkspacePopout";

// todo: these styles seem weird
const cloudWorkspaces = (
  <WorkspacePopout>
    {({ onOpen, value }) => (
      <button className={styles.workspaceButton} onClick={onOpen} data-testid="workspaceButton">
        {value}
      </button>
    )}
  </WorkspacePopout>
);

export const CloudSideBar: React.FC = () => {
  return (
    <GenericSideBar>
      <FlexContainer direction="column" className={styles.menuContent}>
        <AirbyteHomeLink />
        {cloudWorkspaces}
        <FlexContainer
          direction="column"
          alignItems="center"
          justifyContent="space-between"
          className={styles.menuContent}
        >
          <MainNav />
          <CloudBottomItems />
        </FlexContainer>
      </FlexContainer>
    </GenericSideBar>
  );
};
