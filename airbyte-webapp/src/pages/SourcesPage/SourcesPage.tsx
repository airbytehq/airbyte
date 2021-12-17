import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { NetworkErrorBoundary as ErrorBoundary } from "rest-hooks";

import { RoutePaths } from "pages/routes";
import AllSourcesPage from "./pages/AllSourcesPage";
import CreateSourcePage from "./pages/CreateSourcePage";
import SourceItemPage from "./pages/SourceItemPage";
import CreationFormPage from "pages/ConnectionPage/pages/CreationFormPage";

const FallbackRootNavigateor = () => <Navigate to="" />;

const SourcesPage: React.FC = () => (
  <Routes>
    <Route path={RoutePaths.SourceNew} element={<CreateSourcePage />} />
    <Route path={RoutePaths.ConnectionNew} element={<CreationFormPage />} />
    <Route
      path=":id"
      element={
        <ErrorBoundary fallbackComponent={FallbackRootNavigateor}>
          <SourceItemPage />
        </ErrorBoundary>
      }
    />
    <Route index element={<AllSourcesPage />} />
    <Route element={<Navigate to="" />} />
  </Routes>
);

export default SourcesPage;
