import React from "react";

import { LoadingPage } from "components";
import { FlexContainer } from "components/ui/Flex";

import { useConfig } from "config";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

import styles from "./MainView.module.scss";
import { AirbyteHomeLink } from "../SideBar/AirbyteHomeLink";
import { BottomItems } from "../SideBar/BottomItems";
import { MenuContent } from "../SideBar/components/MenuContent";
import { MainNavItems } from "../SideBar/MainNavItems";
import { SideBar } from "../SideBar/SideBar";

const MainView: React.FC<React.PropsWithChildren<unknown>> = (props) => {
  const { version } = useConfig();

  return (
    <FlexContainer className={styles.mainViewContainer}>
      <SideBar>
        <AirbyteHomeLink />
        <MenuContent>
          <MainNavItems />
          <BottomItems version={version} />
        </MenuContent>
      </SideBar>
      <div className={styles.content}>
        <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
          <React.Suspense fallback={<LoadingPage />}>{props.children}</React.Suspense>
        </ResourceNotFoundErrorBoundary>
      </div>
    </FlexContainer>
  );
};

export default MainView;
