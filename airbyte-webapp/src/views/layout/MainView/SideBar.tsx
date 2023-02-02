import { useConfig } from "config";

import { AirbyteHomeLink } from "../SideBar/AirbyteHomeLink";
import { BottomItems } from "../SideBar/BottomItems";
import { MenuContent } from "../SideBar/components/MenuContent";
import { GenericSideBar } from "../SideBar/GenericSideBar";
import { MainNav } from "../SideBar/MainNav";

export const SideBar: React.FC = () => {
  const { version } = useConfig();

  return (
    <GenericSideBar>
      <AirbyteHomeLink />
      <MenuContent>
        <MainNav />
        <BottomItems version={version} />
      </MenuContent>
    </GenericSideBar>
  );
};
