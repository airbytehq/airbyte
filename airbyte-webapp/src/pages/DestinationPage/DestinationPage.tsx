import React from "react";
import { Route, Routes } from "react-router-dom";

import { RoutePaths } from "../routes";
import AllDestinationsPage from "./pages/AllDestinationsPage";
import DestinationItemPage from "./pages/DestinationItemPage";
import CreateDestinationPage from "./pages/CreateDestinationPage";
import CreationFormPage from "../ConnectionPage/pages/CreationFormPage";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

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
          <ResourceNotFoundErrorBoundary
            errorComponent={<StartOverErrorView />}
          >
            <DestinationItemPage />
          </ResourceNotFoundErrorBoundary>
        }
      />
      <Route index element={<AllDestinationsPage />} />
    </Routes>
  );
};

export default DestinationsPage;
