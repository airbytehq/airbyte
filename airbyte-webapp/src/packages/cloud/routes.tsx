import React, { Suspense } from "react";
import {
  BrowserRouter as Router,
  Redirect,
  Route,
  Switch,
} from "react-router-dom";

import config from "config";

import SourcesPage from "pages/SourcesPage";
import DestinationPage from "pages/DestinationPage";
import ConnectionPage from "pages/ConnectionPage";
import SettingsPage from "pages/SettingsPage";
import LoadingPage from "components/LoadingPage";
import MainView from "components/MainView";
import { WorkspacesPage } from "./views/workspaces";
import { useApiHealthPoll } from "components/hooks/services/Health";
import { Auth } from "./views/auth";
import { useAuthService } from "./services/auth/AuthService";

import {
  useGetWorkspace,
  useWorkspaceService,
  WorkspaceServiceProvider,
} from "./services/workspaces/WorkspacesService";
import { HealthService } from "core/health/HealthService";
import { useDefaultRequestMiddlewares } from "./services/workspaces/useDefaultRequestMiddlewares";

export enum Routes {
  Preferences = "/preferences",
  Onboarding = "/onboarding",

  Connections = "/connections",
  Destination = "/destination",
  Source = "/source",
  Connection = "/connection",
  ConnectionNew = "/new-connection",
  SourceNew = "/new-source",
  DestinationNew = "/new-destination",
  Settings = "/settings",
  Configuration = "/configuration",
  Notifications = "/notifications",
  Metrics = "/metrics",
  Account = "/account",
  Workspaces = "/workspaces",
  Signup = "/signup",
  Login = "/login",
  ResetPassword = "/reset-password",
  Root = "/",
  SelectWorkspace = "/workspaces",
}

const MainRoutes: React.FC<{ currentWorkspaceId: string }> = ({
  currentWorkspaceId,
}) => {
  useGetWorkspace(currentWorkspaceId);

  return (
    <Switch>
      <Route path={Routes.Destination}>
        <DestinationPage />
      </Route>
      <Route path={Routes.Source}>
        <SourcesPage />
      </Route>
      <Route path={Routes.Connections}>
        <ConnectionPage />
      </Route>
      <Route path={Routes.Settings}>
        <SettingsPage />
      </Route>
      <Route path={Routes.Workspaces}>
        <WorkspacesPage />
      </Route>
      <Route exact path={Routes.Root}>
        <SourcesPage />
      </Route>
      <Redirect to={Routes.Connections} />
    </Switch>
  );
};

const MainViewRoutes = () => {
  const middlewares = useDefaultRequestMiddlewares();

  useApiHealthPoll(config.healthCheckInterval, new HealthService(middlewares));
  const { currentWorkspaceId } = useWorkspaceService();

  return (
    <>
      {currentWorkspaceId ? (
        <MainView>
          <Suspense fallback={<LoadingPage />}>
            <MainRoutes currentWorkspaceId={currentWorkspaceId} />
          </Suspense>
        </MainView>
      ) : (
        <Switch>
          <Route exact path={Routes.SelectWorkspace}>
            <WorkspacesPage />
          </Route>
          <Redirect to={Routes.SelectWorkspace} />
        </Switch>
      )}
    </>
  );
};

export const Routing: React.FC = () => {
  const { user, inited } = useAuthService();
  return (
    <Router>
      <Suspense fallback={<LoadingPage />}>
        {inited ? (
          <>
            {user && (
              <WorkspaceServiceProvider>
                <MainViewRoutes />
              </WorkspaceServiceProvider>
            )}
            {!user && <Auth />}
          </>
        ) : (
          <LoadingPage />
        )}
      </Suspense>
    </Router>
  );
};
