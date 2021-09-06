import React, { Suspense } from "react";
import { Redirect, Route, Switch } from "react-router-dom";
import { NetworkErrorBoundary as ErrorBoundary } from "rest-hooks";

import { Routes } from "../routes";
import LoadingPage from "components/LoadingPage";
import ConnectionItemPage from "./pages/ConnectionItemPage";
import CreationFormPage from "./pages/CreationFormPage";
import useRouter from "hooks/useRouter";
import AllConnectionsPage from "./pages/AllConnectionsPage";

const FallbackRootRedirector = () => <Redirect to={Routes.Root} />;

const ConnectionPage: React.FC = () => {
  const { location } = useRouter();

  return (
    <Suspense fallback={<LoadingPage />}>
      <Switch>
        <Route
          path={[
            `${Routes.Connections}${Routes.ConnectionNew}`,
            `${Routes.Source}${Routes.ConnectionNew}`,
            `${Routes.Destination}${Routes.ConnectionNew}`,
          ]}
        >
          <CreationFormPage
            type={
              location.pathname ===
              `${Routes.Connections}${Routes.ConnectionNew}`
                ? "connection"
                : location.pathname ===
                  `${Routes.Source}${Routes.ConnectionNew}`
                ? "destination"
                : "source"
            }
          />
        </Route>
        <Route path={`${Routes.Connections}/:id${Routes.Settings}`}>
          <ErrorBoundary fallbackComponent={FallbackRootRedirector}>
            <ConnectionItemPage currentStep="settings" />
          </ErrorBoundary>
        </Route>
        <Route path={`${Routes.Connections}/:id`}>
          <ErrorBoundary fallbackComponent={FallbackRootRedirector}>
            <ConnectionItemPage currentStep="status" />
          </ErrorBoundary>
        </Route>
        <Route path={Routes.Connections}>
          <AllConnectionsPage />
        </Route>
        <Redirect to={Routes.Root} />
      </Switch>
    </Suspense>
  );
};

export default ConnectionPage;
