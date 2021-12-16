import React, { Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { NetworkErrorBoundary as ErrorBoundary } from "rest-hooks";

import { RoutePaths } from "../routes";
import LoadingPage from "components/LoadingPage";
import ConnectionItemPage from "./pages/ConnectionItemPage";
import CreationFormPage from "./pages/CreationFormPage";
import AllConnectionsPage from "./pages/AllConnectionsPage";

const FallbackRootNavigateor = () => <Navigate to={RoutePaths.Root} />;

const ConnectionPage: React.FC = () => {
  return (
    <Suspense fallback={<LoadingPage />}>
      <Routes>
        <Route path={RoutePaths.ConnectionNew} element={<CreationFormPage />} />
        <Route
          path=":id/*"
          element={
            <ErrorBoundary fallbackComponent={FallbackRootNavigateor}>
              <ConnectionItemPage />
            </ErrorBoundary>
          }
        />
        <Route index element={<AllConnectionsPage />} />
      </Routes>
    </Suspense>
  );
};

export default ConnectionPage;
