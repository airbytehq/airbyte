import React, { Suspense } from "react";
import { Redirect, Route, Switch } from "react-router-dom";
import { NetworkErrorBoundary as ErrorBoundary } from "rest-hooks";

import { Routes } from "../routes";
import LoadingPage from "components/LoadingPage";
import AllDestinationsPage from "./pages/AllDestinationsPage";
import DestinationItemPage from "./pages/DestinationItemPage";
import CreateDestinationPage from "./pages/CreateDestinationPage";
import ConnectionPage from "../ConnectionPage";

const FallbackRootRedirector = () => <Redirect to={Routes.Destination} />;

const DestinationsPage: React.FC = () => {
  return (
    <Suspense fallback={<LoadingPage />}>
      <Switch>
        <Route path={`${Routes.Destination}${Routes.DestinationNew}`}>
          <CreateDestinationPage />
        </Route>
        <Route path={Routes.Destination} exact>
          <AllDestinationsPage />
        </Route>
        <Route
          path={[
            `${Routes.Destination}${Routes.ConnectionNew}`,
            `${Routes.Destination}${Routes.Connection}/:id`,
          ]}
        >
          <ConnectionPage />
        </Route>
        <Route path={`${Routes.Destination}/:id`}>
          <ErrorBoundary fallbackComponent={FallbackRootRedirector}>
            <DestinationItemPage />
          </ErrorBoundary>
        </Route>
        <Redirect to={Routes.Root} />
      </Switch>
    </Suspense>
  );
};

export default DestinationsPage;
