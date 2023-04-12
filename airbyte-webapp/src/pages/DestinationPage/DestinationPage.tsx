import React, { Suspense, lazy } from "react";
import { Route, Routes } from "react-router-dom";

import { LoadingPage } from "components";

import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

import { RoutePaths } from "../routePaths";

const CreationFormPage = lazy(() => import("pages/ConnectionPage/pages/CreationFormPage"));
const SelectConnectionPage = lazy(() => import("pages/ConnectionPage/pages/CreationFormPage/SelectConnectionPage"));
const AllDestinationsPage = lazy(() => import("./pages/AllDestinationsPage"));
const CopyDestinationPage = lazy(() => import("./pages/CopyDestinationPage"));
const CreateDestinationPage = lazy(() => import("./pages/CreateDestinationPage"));
const SelectDestinationPage = lazy(() => import("./pages/CreateDestinationPage/SelectDestinationPage"));
const DestinationItemPage = lazy(() => import("./pages/DestinationItemPage"));

const DestinationsPage: React.FC = () => {
  return (
    <Suspense fallback={<LoadingPage position="relative" />}>
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
    </Suspense>
  );
};

export default DestinationsPage;
