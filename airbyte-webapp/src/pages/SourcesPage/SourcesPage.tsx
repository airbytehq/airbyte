import React, { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { LoadingPage } from "components";

import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

import { RoutePaths } from "../routePaths";

const CreationFormPage = lazy(() => import("pages/ConnectionPage/pages/CreationFormPage"));
const SelectConnetionPage = lazy(() => import("pages/ConnectionPage/pages/CreationFormPage/SelectConnectionPage"));
const AllSourcesPage = lazy(() => import("./pages/AllSourcesPage"));
const CopySourcePage = lazy(() => import("./pages/CopySourcePage/"));
const CreateSourcePage = lazy(() => import("./pages/CreateSourcePage/CreateSourcePage"));
const SelectSourcePage = lazy(() => import("./pages/CreateSourcePage/SelectSourcePage"));
const SourceItemPage = lazy(() => import("./pages/SourceItemPage"));

export const SourcesPage: React.FC = () => (
  <Suspense fallback={<LoadingPage position="relative" />}>
    <Routes>
      <Route path={RoutePaths.SourceNew} element={<CreateSourcePage />} />
      <Route path={RoutePaths.ConnectionNew} element={<CreationFormPage backtrack />} />
      <Route path={RoutePaths.SelectConnection} element={<SelectConnetionPage backtrack />} />
      <Route path={RoutePaths.SelectSource} element={<SelectSourcePage />} />
      <Route
        path=":id/*"
        element={
          <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
            <SourceItemPage />
          </ResourceNotFoundErrorBoundary>
        }
      />
      <Route path=":id/copy" element={<CopySourcePage />} />
      <Route index element={<AllSourcesPage />} />
      <Route element={<Navigate to="" />} />
    </Routes>
  </Suspense>
);
