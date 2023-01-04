import React, { Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { LoadingPage } from "components";

import { RoutePaths } from "../routePaths";
import { AllConnectionsPage } from "./AllConnectionsPage";
import { ConnectionPage } from "./ConnectionPage/ConnectionPage";
import { ConnectionReplicationPage } from "./ConnectionReplicationPage";
import { ConnectionSettingsPage } from "./ConnectionSettingsPage";
import { ConnectionStatusPage } from "./ConnectionStatusPage";
import { ConnectionTransformationPage } from "./ConnectionTransformationPage";
import { CreateConnectionPage } from "./CreateConnectionPage/CreateConnectionPage";
import { ConnectionRoutePaths } from "./types";

export const ConnectionsRoutes: React.FC = () => (
  <Suspense fallback={<LoadingPage />}>
    <Routes>
      <Route path={RoutePaths.ConnectionNew} element={<CreateConnectionPage />} />
      <Route path={ConnectionRoutePaths.Root} element={<ConnectionPage />}>
        <Route path={ConnectionRoutePaths.Status} element={<ConnectionStatusPage />} />
        <Route path={ConnectionRoutePaths.Replication} element={<ConnectionReplicationPage />} />
        <Route path={ConnectionRoutePaths.Transformation} element={<ConnectionTransformationPage />} />
        <Route path={ConnectionRoutePaths.Settings} element={<ConnectionSettingsPage />} />
        <Route index element={<Navigate to={ConnectionRoutePaths.Status} replace />} />
      </Route>
      <Route index element={<AllConnectionsPage />} />
    </Routes>
  </Suspense>
);
