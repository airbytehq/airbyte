import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

import { RoutePaths } from "../routePaths";

const AllSourcesPage = React.lazy(() => import("./pages/AllSourcesPage"));
const CreateSourcePage = React.lazy(() => import("./pages/CreateSourcePage/CreateSourcePage"));
const SourceItemPage = React.lazy(() => import("./pages/SourceItemPage"));
const CreateConnectionPage = React.lazy(() => import("pages/connections/CreateConnectionPage"));

export const SourcesPage: React.FC = () => (
  <Routes>
    <Route path={RoutePaths.SourceNew} element={<CreateSourcePage />} />
    <Route path={RoutePaths.ConnectionNew} element={<CreateConnectionPage />} />
    <Route
      path=":id/*"
      element={
        <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
          <SourceItemPage />
        </ResourceNotFoundErrorBoundary>
      }
    />
    <Route index element={<AllSourcesPage />} />
    <Route element={<Navigate to="" />} />
  </Routes>
);
