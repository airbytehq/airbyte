import { FlexContainer } from "components/ui/Flex";

import { useConfig } from "config";

import styles from "./SideBar.module.scss";
import { AirbyteHomeLink } from "../SideBar/AirbyteHomeLink";
import { BottomItems } from "../SideBar/BottomItems";
import { GenericSideBar } from "../SideBar/GenericSideBar";
import { MainNav } from "../SideBar/MainNav";

export const SideBar: React.FC = () => {
  const { version } = useConfig();

  return (
    <GenericSideBar>
      <FlexContainer direction="column" className={styles.menuContent}>
        <AirbyteHomeLink />
        <FlexContainer
          direction="column"
          alignItems="center"
          justifyContent="space-between"
          className={styles.menuContent}
        >
          <MainNav />
          <BottomItems version={version} />
        </FlexContainer>
      </FlexContainer>
    </GenericSideBar>
  );
};
