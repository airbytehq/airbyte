import { FormattedMessage } from "react-intl";

import { RoutePaths } from "pages/routePaths";

import ConnectionsIcon from "./components/ConnectionsIcon";
import DestinationIcon from "./components/DestinationIcon";
import { MenuContent } from "./components/MenuContent";
import { NavItem } from "./components/NavItem";
import SourceIcon from "./components/SourceIcon";

export const MainNavItems: React.FC = () => {
  return (
    <ul data-testid="navMainItems">
      <MenuContent>
        <li>
          <NavItem
            label={<FormattedMessage id="sidebar.connections" />}
            icon={<ConnectionsIcon />}
            to={RoutePaths.Connections}
            testId="connectionsLink"
          />
        </li>
        <li>
          <NavItem
            label={<FormattedMessage id="sidebar.sources" />}
            icon={<SourceIcon />}
            to={RoutePaths.Source}
            testId="sourcesLink"
          />
        </li>
        <li>
          <NavItem
            label={<FormattedMessage id="sidebar.destinations" />}
            icon={<DestinationIcon />}
            testId="destinationsLink"
            to={RoutePaths.Destination}
          />
        </li>
      </MenuContent>
    </ul>
  );
};
