import { FormattedMessage } from "react-intl";

import { FlexContainer } from "components/ui/Flex";

import { RoutePaths } from "pages/routePaths";

import ConnectionsIcon from "./components/ConnectionsIcon";
import DestinationIcon from "./components/DestinationIcon";
import { NavItem } from "./components/NavItem";
import SourceIcon from "./components/SourceIcon";
import styles from "./MainNav.module.scss";

export const MainNav: React.FC = () => {
  return (
    <ul data-testid="navMainItems">
      <FlexContainer direction="column" gap="sm" className={styles.menuContent}>
        <li>
          <NavItem
            as="navLink"
            label={<FormattedMessage id="sidebar.connections" />}
            icon={<ConnectionsIcon />}
            to={RoutePaths.Connections}
            testId="connectionsLink"
          />
        </li>
        <li>
          <NavItem
            as="navLink"
            label={<FormattedMessage id="sidebar.sources" />}
            icon={<SourceIcon />}
            to={RoutePaths.Source}
            testId="sourcesLink"
          />
        </li>
        <li>
          <NavItem
            as="navLink"
            label={<FormattedMessage id="sidebar.destinations" />}
            icon={<DestinationIcon />}
            testId="destinationsLink"
            to={RoutePaths.Destination}
          />
        </li>
      </FlexContainer>
    </ul>
  );
};
