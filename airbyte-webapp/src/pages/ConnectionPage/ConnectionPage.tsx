import React, { Suspense } from "react";
import { Route, Routes } from "react-router-dom";

import { RoutePaths } from "../routes";
import LoadingPage from "components/LoadingPage";
import ConnectionItemPage from "./pages/ConnectionItemPage";
import CreationFormPage from "./pages/CreationFormPage";
import AllConnectionsPage from "./pages/AllConnectionsPage";
import { StartOverErrorView } from "views/common/StartOverErrorView";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";

const ConnectionPage: React.FC = () => {
  return (
    <Suspense fallback={<LoadingPage />}>
      <Routes>
        <Route path={RoutePaths.ConnectionNew} element={<CreationFormPage />} />
        <Route
          path=":id/*"
          element={
            <ResourceNotFoundErrorBoundary
              errorComponent={<StartOverErrorView />}
            >
              <ConnectionItemPage />
            </ResourceNotFoundErrorBoundary>
          }
        />
        <Route index element={<AllConnectionsPage />} />
      </Routes>
    </Suspense>
  );
};

export default ConnectionPage;
