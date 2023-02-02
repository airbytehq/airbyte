import { faRocket } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormattedMessage } from "react-intl";

import { Version } from "components/common/Version";
import { FlexContainer } from "components/ui/Flex";

import { RoutePaths } from "pages/routePaths";
import { links } from "utils/links";

import styles from "./BottomItems.module.scss";
import { NavItem } from "./components/NavItem";
import { ResourcesDropdown } from "./components/ResourcesDropdown";
import SettingsIcon from "./components/SettingsIcon";

interface BottomItemProps {
  version: string;
}
export const BottomItems: React.FC<BottomItemProps> = ({ version }) => {
  return (
    <ul>
      <FlexContainer direction="column" gap="xs" className={styles.menuContent}>
        <li>
          <NavItem
            as="a"
            to={links.updateLink}
            icon={<FontAwesomeIcon className={styles.helpIcon} icon={faRocket} />}
            label={<FormattedMessage id="sidebar.update" />}
            testId="updateLink"
          />
        </li>
        <li>
          <ResourcesDropdown />
        </li>
        <li>
          <NavItem
            as="navLink"
            label={<FormattedMessage id="sidebar.settings" />}
            icon={<SettingsIcon />}
            to={RoutePaths.Settings}
            withNotification
          />
        </li>
        {version && <Version primary />}
      </FlexContainer>
    </ul>
  );
};
