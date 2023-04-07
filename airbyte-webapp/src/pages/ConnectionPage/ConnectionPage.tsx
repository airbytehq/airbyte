import React, { Suspense, lazy } from "react";
import { Route, Routes } from "react-router-dom";

import { LoadingPage } from "components";

import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

import { RoutePaths } from "../routePaths";

const AllConnectionsPage = lazy(() => import("./pages/AllConnectionsPage"));
const SelectConnectionCard = lazy(() => import("pages/ConnectionPage/pages/CreationFormPage/SelectConnectionPage"));
const ConnectionItemPage = lazy(() => import("./pages/ConnectionItemPage"));
const CreationFormPage = lazy(() => import("./pages/CreationFormPage"));

export const ConnectionPage: React.FC = () => (
  <Suspense fallback={<LoadingPage position="relative" />}>
    <Routes>
      <Route path={RoutePaths.ConnectionNew} element={<CreationFormPage />} />
      <Route path={RoutePaths.SelectConnection} element={<SelectConnectionCard />} />
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
