import { FormattedMessage } from "react-intl";

import { useExperiment } from "hooks/services/Experiment";
import { RoutePaths } from "pages/routePaths";

import BuilderIcon from "./components/BuilderIcon";
import ConnectionsIcon from "./components/ConnectionsIcon";
import DestinationIcon from "./components/DestinationIcon";
import { MenuContent } from "./components/MenuContent";
import { NavItem } from "./components/NavItem";
import SourceIcon from "./components/SourceIcon";

export const MainNavItems: React.FC = () => {
  const showBuilderNavigationLinks = useExperiment("connectorBuilder.showNavigationLinks", false);

  return (
    <MenuContent data-testid="navMainItems">
      <NavItem
        label={<FormattedMessage id="sidebar.connections" />}
        icon={<ConnectionsIcon />}
        to={RoutePaths.Connections}
        testId="connectionsLink"
      />

      <NavItem
        label={<FormattedMessage id="sidebar.sources" />}
        icon={<SourceIcon />}
        to={RoutePaths.Source}
        testId="sourcesLink"
      />

      <NavItem
        label={<FormattedMessage id="sidebar.destinations" />}
        icon={<DestinationIcon />}
        testId="destinationsLink"
        to={RoutePaths.Destination}
      />
      {showBuilderNavigationLinks && (
        <NavItem
          label={<FormattedMessage id="sidebar.builder" />}
          icon={<BuilderIcon />}
          testId="builderLink"
          to={RoutePaths.ConnectorBuilder}
        />
      )}
    </MenuContent>
  );
};
