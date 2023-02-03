import { faRocket } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormattedMessage } from "react-intl";

import { Version } from "components/common/Version";

import { RoutePaths } from "pages/routePaths";
import { links } from "utils/links";

import { MenuContent } from "./components/MenuContent";
import { NavItem } from "./components/NavItem";
import { ResourcesDropdown } from "./components/ResourcesDropdown";
import SettingsIcon from "./components/SettingsIcon";

/**
 * Bottom items of the sidebar for OSS.
 * Cloud maintains a separate version of this component titled "CloudBottomItems"
 */

interface BottomItemProps {
  version: string;
}
export const BottomItems: React.FC<BottomItemProps> = ({ version }) => {
  return (
    <ul>
      <MenuContent>
        <li>
          <NavItem
            as="a"
            to={links.updateLink}
            icon={<FontAwesomeIcon icon={faRocket} />}
            label={<FormattedMessage id="sidebar.update" />}
            testId="updateLink"
          />
        </li>
        <li>
          <ResourcesDropdown />
        </li>
        <li>
          <NavItem
            label={<FormattedMessage id="sidebar.settings" />}
            icon={<SettingsIcon />}
            to={RoutePaths.Settings}
            withNotification
          />
        </li>
        {version && <Version primary />}
      </MenuContent>
    </ul>
  );
};
