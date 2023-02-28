import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { CreationFormPage } from "pages/ConnectionPage/pages/CreationFormPage/CreationFormPage";
import SelectConnetionPage from "pages/ConnectionPage/pages/CreationFormPage/SelectConnectionPage";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

import { RoutePaths } from "../routePaths";
import AllSourcesPage from "./pages/AllSourcesPage";
import CopySourcePage from "./pages/CopySourcePage/";
import CreateSourcePage from "./pages/CreateSourcePage/CreateSourcePage";
import SelectSourcePage from "./pages/CreateSourcePage/SelectSourcePage";
import SourceItemPage from "./pages/SourceItemPage";

export const SourcesPage: React.FC = () => (
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
);
