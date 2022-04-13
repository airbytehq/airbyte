import React, { Suspense } from "react";
import { Route, Routes } from "react-router-dom";

import { LoadingPage } from "components";

import { StartOverErrorView } from "views/common/StartOverErrorView";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";

import { RoutePaths } from "../routePaths";
import ConnectionItemPage from "./pages/ConnectionItemPage";
import CreationFormPage from "./pages/CreationFormPage";
import AllConnectionsPage from "./pages/AllConnectionsPage";

const ConnectionPage: React.FC = () => (
  <Suspense fallback={<LoadingPage />}>
    <Routes>
      <Route path={RoutePaths.ConnectionNew} element={<CreationFormPage />} />
      <Route
        path=":connectionId/*"
        element={
          <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
            <ConnectionItemPage />
          </ResourceNotFoundErrorBoundary>
        }
      />
      <Route index element={<AllConnectionsPage />} />
    </Routes>
  </Suspense>
);

export default ConnectionPage;
