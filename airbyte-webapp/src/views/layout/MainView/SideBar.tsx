import { FlexContainer } from "components/ui/Flex";

import styles from "./SideBar.module.scss";
import { GenericSideBar } from "../SideBar/GenericSideBar";
import { MainNav } from "../SideBar/MainNav";
import { TopItems } from "../SideBar/TopItems";

export const SideBar: React.FC = () => {
  return (
    <GenericSideBar>
      <FlexContainer direction="column">
        <TopItems />
        <FlexContainer
          direction="column"
          alignItems="center"
          justifyContent="space-between"
          className={styles.menuContent}
        >
          <TopItems />
          <MainNav />
          {/* <BottomItems /> */}
        </FlexContainer>
      </FlexContainer>
    </GenericSideBar>
  );
};
