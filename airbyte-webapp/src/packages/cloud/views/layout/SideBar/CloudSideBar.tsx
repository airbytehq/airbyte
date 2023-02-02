import React from "react";

import { FlexContainer } from "components/ui/Flex";

import { AirbyteHomeLink } from "views/layout/SideBar/AirbyteHomeLink";
import { MenuContent } from "views/layout/SideBar/components/MenuContent";
import { GenericSideBar } from "views/layout/SideBar/GenericSideBar";
import { MainNav } from "views/layout/SideBar/MainNav";

import { CloudBottomItems } from "./CloudBottomItems";
import styles from "./CloudSideBar.module.scss";
import { WorkspacePopout } from "../../workspaces/WorkspacePopout";

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
      <MenuContent>
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
      </MenuContent>
    </GenericSideBar>
  );
};
