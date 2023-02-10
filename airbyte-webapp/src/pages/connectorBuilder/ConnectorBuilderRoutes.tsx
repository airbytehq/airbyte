import { Suspense } from "react";
import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { LoadingPage } from "components";

const ConnectorBuilderLandingPage = React.lazy(() => import("./ConnectorBuilderLandingPage"));
const ConnectorBuilderEditPage = React.lazy(() => import("./ConnectorBuilderEditPage"));

export const enum ConnectorBuilderRoutePaths {
  Edit = "edit",
}

const ConnectorBuilderRoutes: React.FC = () => (
  <Suspense fallback={<LoadingPage />}>
    <Routes>
      <Route path={ConnectorBuilderRoutePaths.Edit} element={<ConnectorBuilderEditPage />} />
      <Route index element={<ConnectorBuilderLandingPage />} />
      <Route path="*" element={<Navigate to="." replace />} />
    </Routes>
  </Suspense>
);

export default ConnectorBuilderRoutes;
