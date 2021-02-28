import React, { Suspense } from "react";
import { Redirect, Route, Switch } from "react-router-dom";
import { NetworkErrorBoundary as ErrorBoundary } from "rest-hooks";

import { Routes } from "../routes";
import LoadingPage from "components/LoadingPage";
import ConnectionItemPage from "./pages/ConnectionItemPage";
import CreationFormPage from "./pages/CreationFormPage";
import useRouter from "components/hooks/useRouterHook";

const FallbackRootRedirector = () => <Redirect to={Routes.Root} />;

const ConnectionPage: React.FC = () => {
  const { location } = useRouter();

  return (
    <Suspense fallback={<LoadingPage />}>
      <Switch>
        <Route
          path={[
            `${Routes.Source}${Routes.ConnectionNew}`,
            `${Routes.Destination}${Routes.ConnectionNew}`,
          ]}
        >
          <CreationFormPage
            type={
              location.pathname === `${Routes.Source}${Routes.ConnectionNew}`
                ? "destination"
                : "source"
            }
          />
        </Route>
        <Route
          path={[
            `${Routes.Source}${Routes.Connection}/:id`,
            `${Routes.Destination}${Routes.Connection}/:id`,
          ]}
        >
          <ErrorBoundary fallbackComponent={FallbackRootRedirector}>
            <ConnectionItemPage />
          </ErrorBoundary>
        </Route>
        <Redirect to={Routes.Root} />
      </Switch>
    </Suspense>
  );
};

export default ConnectionPage;
