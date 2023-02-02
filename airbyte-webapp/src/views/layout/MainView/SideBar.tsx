import { useConfig } from "config";

import { AirbyteHomeLink } from "../SideBar/AirbyteHomeLink";
import { BottomItems } from "../SideBar/BottomItems";
import { MenuContent } from "../SideBar/components/MenuContent";
import { GenericSideBar } from "../SideBar/GenericSideBar";
import { MainNavItems } from "../SideBar/MainNavItems";

export const SideBar: React.FC = () => {
  const { version } = useConfig();

  return (
    <GenericSideBar>
      <AirbyteHomeLink />
      <MenuContent>
        <MainNavItems />
        <BottomItems version={version} />
      </MenuContent>
    </GenericSideBar>
  );
};
