import React, { Suspense } from "react";
import { Redirect, Route, Switch } from "react-router-dom";
import { NetworkErrorBoundary as ErrorBoundary } from "rest-hooks";

import { Routes } from "../routes";
import LoadingPage from "components/LoadingPage";
import ConnectionPage from "pages/ConnectionPage";
import AllSourcesPage from "./pages/AllSourcesPage";
import CreateSourcePage from "./pages/CreateSourcePage";
import SourceItemPage from "./pages/SourceItemPage";

const FallbackRootRedirector = () => <Redirect to={Routes.Root} />;

const SourcesPage: React.FC = () => {
  return (
    <Suspense fallback={<LoadingPage />}>
      <Switch>
        <Route path={`${Routes.Source}${Routes.SourceNew}`}>
          <CreateSourcePage />
        </Route>
        <Route
          path={[
            `${Routes.Source}${Routes.ConnectionNew}`,
            `${Routes.Source}${Routes.Connection}/:id`,
          ]}
        >
          <ConnectionPage />
        </Route>
        <Route path={`${Routes.Source}/:id`}>
          <ErrorBoundary fallbackComponent={FallbackRootRedirector}>
            <SourceItemPage />
          </ErrorBoundary>
        </Route>
        <Route path={Routes.Source} exact>
          <AllSourcesPage />
        </Route>
        <Redirect to={Routes.Root} />
      </Switch>
    </Suspense>
  );
};

export default SourcesPage;
