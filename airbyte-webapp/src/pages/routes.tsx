import React, { useMemo } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useEffectOnce } from "react-use";

import { ApiErrorBoundary } from "components/common/ApiErrorBoundary";

import { useAnalyticsIdentifyUser, useAnalyticsRegisterValues } from "hooks/services/Analytics";
import { useApiHealthPoll } from "hooks/services/Health";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useListWorkspaces } from "services/workspaces/WorkspacesService";
import { storeUtmFromQuery } from "utils/utmStorage";
import { CompleteOauthRequest } from "views/CompleteOauthRequest";
import MainView from "views/layout/MainView";

import { WorkspaceRead } from "../core/request/AirbyteClient";
import ConnectionPage from "./ConnectionPage";
import CreationFormPage from "./ConnectionPage/pages/CreationFormPage";
import { ConnectorBuilderPage } from "./ConnectorBuilderPage/ConnectorBuilderPage";
import { AllDestinationsPage } from "./destination/AllDestinationsPage";
import CreateDestinationPage from "./destination/CreateDestinationPage";
import { DestinationItemPage } from "./destination/DestinationItemPage";
import { DestinationOverviewPage } from "./destination/DestinationOverviewPage";
import { DestinationSettingsPage } from "./destination/DestinationSettingsPage";
import PreferencesPage from "./PreferencesPage";
import { RoutePaths, DestinationPaths } from "./routePaths";
import SettingsPage from "./SettingsPage";
import SourcesPage from "./SourcesPage";

const useAddAnalyticsContextForWorkspace = (workspace: WorkspaceRead): void => {
  const analyticsContext = useMemo(
    () => ({
      workspace_id: workspace.workspaceId,
      customer_id: workspace.customerId,
    }),
    [workspace.workspaceId, workspace.customerId]
  );
  useAnalyticsRegisterValues(analyticsContext);
  useAnalyticsIdentifyUser(workspace.workspaceId);
};

const MainViewRoutes: React.FC = () => {
  return (
    <MainView>
      <ApiErrorBoundary>
        <Routes>
          <Route path={RoutePaths.Destination}>
            <Route index element={<AllDestinationsPage />} />
            <Route path={DestinationPaths.NewDestination} element={<CreateDestinationPage />} />
            <Route path={DestinationPaths.NewConnection} element={<CreationFormPage />} />
            <Route path={DestinationPaths.Root} element={<DestinationItemPage />}>
              <Route path={DestinationPaths.Settings} element={<DestinationSettingsPage />} />
              <Route index element={<DestinationOverviewPage />} />
            </Route>
          </Route>
          <Route path={`${RoutePaths.Source}/*`} element={<SourcesPage />} />
          <Route path={`${RoutePaths.Connections}/*`} element={<ConnectionPage />} />
          <Route path={`${RoutePaths.Settings}/*`} element={<SettingsPage />} />
          <Route path={`${RoutePaths.ConnectorBuilder}/*`} element={<ConnectorBuilderPage />} />

          <Route path="*" element={<Navigate to={RoutePaths.Connections} />} />
        </Routes>
      </ApiErrorBoundary>
    </MainView>
  );
};

const PreferencesRoutes = () => (
  <Routes>
    <Route path={RoutePaths.Preferences} element={<PreferencesPage />} />
    <Route path="*" element={<Navigate to={RoutePaths.Preferences} />} />
  </Routes>
);

export const AutoSelectFirstWorkspace: React.FC<{ includePath?: boolean }> = ({ includePath }) => {
  const location = useLocation();
  const workspaces = useListWorkspaces();
  const currentWorkspace = workspaces[0];

  return (
    <Navigate
      to={`/${RoutePaths.Workspaces}/${currentWorkspace.workspaceId}${includePath ? location.pathname : ""}`}
      replace
    />
  );
};

const RoutingWithWorkspace: React.FC = () => {
  const workspace = useCurrentWorkspace();
  useAddAnalyticsContextForWorkspace(workspace);
  useApiHealthPoll();

  return workspace.initialSetupComplete ? <MainViewRoutes /> : <PreferencesRoutes />;
};

export const Routing: React.FC = () => {
  const { search } = useLocation();

  useEffectOnce(() => {
    storeUtmFromQuery(search);
  });

  // TODO: Remove this after it is verified there are no problems with current routing
  const OldRoutes = useMemo(
    () =>
      Object.values(RoutePaths).map((r) => (
        <Route path={`${r}/*`} key={r} element={<AutoSelectFirstWorkspace includePath />} />
      )),
    []
  );
  return (
    <Routes>
      {OldRoutes}
      <Route path={RoutePaths.AuthFlow} element={<CompleteOauthRequest />} />
      <Route path={`${RoutePaths.Workspaces}/:workspaceId/*`} element={<RoutingWithWorkspace />} />
      <Route path="*" element={<AutoSelectFirstWorkspace />} />
    </Routes>
  );
};
