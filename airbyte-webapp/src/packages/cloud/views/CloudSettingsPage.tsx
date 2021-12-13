import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import useConnector from "hooks/services/useConnector";
import { PageConfig } from "pages/SettingsPage/SettingsPage";
import {
  DestinationsPage as SettingsDestinationPage,
  SourcesPage as SettingsSourcesPage,
} from "pages/SettingsPage/pages/ConnectorsPage";
import SettingsPage from "pages/SettingsPage";
import ConfigurationsPage from "pages/SettingsPage/pages/ConfigurationsPage";
import NotificationPage from "pages/SettingsPage/pages/NotificationPage";
import { AccountSettingsView } from "./users/AccountSettingsView";
import { WorkspaceSettingsView } from "./workspaces/WorkspaceSettingsView";
import { UsersSettingsView } from "./users/UsersSettingsView";
import { RoutePaths } from "pages/routes";

const CloudSettingsRoutes = {
  Configuration: "configuration",
  AccessManagement: "access-management",
  Notifications: "notifications",
  Workspace: "workspaces",
  Account: "account",
};

export const CloudSettingsPage: React.FC = () => {
  const { countNewSourceVersion, countNewDestinationVersion } = useConnector();

  const pageConfig = useMemo<PageConfig>(
    () => ({
      menuConfig: [
        {
          category: <FormattedMessage id="settings.userSettings" />,
          routes: [
            {
              path: `${CloudSettingsRoutes.Account}`,
              name: <FormattedMessage id="settings.account" />,
              component: AccountSettingsView,
            },
          ],
        },
        {
          category: <FormattedMessage id="settings.workspaceSettings" />,
          routes: [
            {
              path: `${CloudSettingsRoutes.Workspace}`,
              name: <FormattedMessage id="settings.generalSettings" />,
              component: WorkspaceSettingsView,
            },
            {
              path: `${RoutePaths.Source}`,
              name: <FormattedMessage id="tables.sources" />,
              indicatorCount: countNewSourceVersion,
              component: SettingsSourcesPage,
            },
            {
              path: `${RoutePaths.Destination}`,
              name: <FormattedMessage id="tables.destinations" />,
              indicatorCount: countNewDestinationVersion,
              component: SettingsDestinationPage,
            },
            {
              path: `${CloudSettingsRoutes.Configuration}`,
              name: <FormattedMessage id="admin.configuration" />,
              component: ConfigurationsPage,
            },
            {
              path: `${CloudSettingsRoutes.AccessManagement}`,
              name: <FormattedMessage id="settings.accessManagementSettings" />,
              component: UsersSettingsView,
            },
            {
              path: `${CloudSettingsRoutes.Notifications}`,
              name: <FormattedMessage id="settings.notifications" />,
              component: NotificationPage,
            },
          ],
        },
      ],
    }),
    [countNewSourceVersion, countNewDestinationVersion]
  );

  return <SettingsPage pageConfig={pageConfig} />;
};
