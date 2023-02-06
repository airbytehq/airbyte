import React, { useMemo } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";

import { ApiErrorBoundary } from "components/common/ApiErrorBoundary";

import { useAnalyticsIdentifyUser, useAnalyticsRegisterValues } from "hooks/services/Analytics";
import { useApiHealthPoll } from "hooks/services/Health";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useListWorkspaces } from "services/workspaces/WorkspacesService";
import { CompleteOauthRequest } from "views/CompleteOauthRequest";
import MainView from "views/layout/MainView";

import { RoutePaths, DestinationPaths } from "./routePaths";
import { WorkspaceRead } from "../core/request/AirbyteClient";

const ConnectionsRoutes = React.lazy(() => import("./connections/ConnectionsRoutes"));
const CreateConnectionPage = React.lazy(() => import("./connections/CreateConnectionPage"));
const ConnectorBuilderPage = React.lazy(() => import("./ConnectorBuilderPage/ConnectorBuilderPage"));

const AllDestinationsPage = React.lazy(() => import("./destination/AllDestinationsPage"));
const CreateDestinationPage = React.lazy(() => import("./destination/CreateDestinationPage"));
const DestinationItemPage = React.lazy(() => import("./destination/DestinationItemPage"));
const DestinationOverviewPage = React.lazy(() => import("./destination/DestinationOverviewPage"));
const DestinationSettingsPage = React.lazy(() => import("./destination/DestinationSettingsPage"));
const PreferencesPage = React.lazy(() => import("./PreferencesPage"));
const SettingsPage = React.lazy(() => import("./SettingsPage"));
const SourcesPage = React.lazy(() => import("./SourcesPage"));

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
            <Route path={DestinationPaths.NewConnection} element={<CreateConnectionPage />} />
            <Route path={DestinationPaths.Root} element={<DestinationItemPage />}>
              <Route path={DestinationPaths.Settings} element={<DestinationSettingsPage />} />
              <Route index element={<DestinationOverviewPage />} />
            </Route>
          </Route>
          <Route path={`${RoutePaths.Source}/*`} element={<SourcesPage />} />
          <Route path={`${RoutePaths.Connections}/*`} element={<ConnectionsRoutes />} />
          <Route path={`${RoutePaths.Settings}/*`} element={<SettingsPage />} />

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

const RoutingWithWorkspace: React.FC<{ element?: JSX.Element }> = ({ element }) => {
  const workspace = useCurrentWorkspace();
  useAddAnalyticsContextForWorkspace(workspace);
  useApiHealthPoll();

  return workspace.initialSetupComplete ? element ?? <MainViewRoutes /> : <PreferencesRoutes />;
};

export const Routing: React.FC = () => {
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
      <Route
        path={`${RoutePaths.Workspaces}/:workspaceId/${RoutePaths.ConnectorBuilder}`}
        element={<RoutingWithWorkspace element={<ConnectorBuilderPage />} />}
      />
      <Route path={`${RoutePaths.ConnectorBuilder}/*`} element={<AutoSelectFirstWorkspace includePath />} />
      {OldRoutes}
      <Route path={RoutePaths.AuthFlow} element={<CompleteOauthRequest />} />
      <Route path={`${RoutePaths.Workspaces}/:workspaceId/*`} element={<RoutingWithWorkspace />} />
      <Route path="*" element={<AutoSelectFirstWorkspace />} />
    </Routes>
  );
};
