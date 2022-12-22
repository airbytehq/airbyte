import React, { Suspense } from "react";
import { Route, Routes } from "react-router-dom";

import { LoadingPage } from "components";

import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

import { RoutePaths } from "../routePaths";
import { AllConnectionsPage } from "./AllConnectionsPage";
import { ConnectionPage } from "./ConnectionPage/ConnectionPage";
import { CreateConnectionPage } from "./CreateConnectionPage/CreateConnectionPage";

export const ConnectionRoutes: React.FC = () => (
  <Suspense fallback={<LoadingPage />}>
    <Routes>
      <Route path={RoutePaths.ConnectionNew} element={<CreateConnectionPage />} />
      <Route
        path=":connectionId/*"
        element={
          <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
            <ConnectionPage />
          </ResourceNotFoundErrorBoundary>
        }
      />
      <Route index element={<AllConnectionsPage />} />
    </Routes>
  </Suspense>
);
