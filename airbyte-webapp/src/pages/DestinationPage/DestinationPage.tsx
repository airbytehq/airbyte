import React from "react";
import { Route, Routes } from "react-router-dom";

import { CreationFormPage } from "pages/ConnectionPage/pages/CreationFormPage/CreationFormPage";
import SelectConnectionPage from "pages/ConnectionPage/pages/CreationFormPage/SelectConnectionPage";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

import { RoutePaths } from "../routePaths";
import AllDestinationsPage from "./pages/AllDestinationsPage";
import CopyDestinationPage from "./pages/CopyDestinationPage";
import { CreateDestinationPage } from "./pages/CreateDestinationPage/CreateDestinationPage";
import SelectDestinationPage from "./pages/CreateDestinationPage/SelectDestinationPage";
import DestinationItemPage from "./pages/DestinationItemPage";

const DestinationsPage: React.FC = () => {
  return (
    <Routes>
      <Route path={RoutePaths.DestinationNew} element={<CreateDestinationPage />} />
      <Route path={RoutePaths.ConnectionNew} element={<CreationFormPage backtrack />} />
      <Route path={RoutePaths.SelectConnection} element={<SelectConnectionPage backtrack />} />
      <Route path={RoutePaths.SelectDestination} element={<SelectDestinationPage />} />
      <Route
        path=":id/*"
        element={
          <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
            <DestinationItemPage />
          </ResourceNotFoundErrorBoundary>
        }
      />
      <Route
        path=":id/copy"
        element={
          <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
            <CopyDestinationPage />
          </ResourceNotFoundErrorBoundary>
        }
      />
      <Route index element={<AllDestinationsPage />} />
    </Routes>
  );
};

export default DestinationsPage;
