import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { NetworkErrorBoundary as ErrorBoundary } from "rest-hooks";

import { RoutePaths } from "../routes";
import AllDestinationsPage from "./pages/AllDestinationsPage";
import DestinationItemPage from "./pages/DestinationItemPage";
import CreateDestinationPage from "./pages/CreateDestinationPage";
import CreationFormPage from "../ConnectionPage/pages/CreationFormPage";

const FallbackRootNavigateor = () => <Navigate to={RoutePaths.Destination} />;

const DestinationsPage: React.FC = () => {
  return (
    <Routes>
      <Route
        path={RoutePaths.DestinationNew}
        element={<CreateDestinationPage />}
      />
      <Route path={RoutePaths.ConnectionNew} element={<CreationFormPage />} />
      <Route
        path=":id"
        element={
          <ErrorBoundary fallbackComponent={FallbackRootNavigateor}>
            <DestinationItemPage />
          </ErrorBoundary>
        }
      />
      <Route index element={<AllDestinationsPage />} />
      <Route element={<Navigate to={RoutePaths.Root} />} />
    </Routes>
  );
};

export default DestinationsPage;
