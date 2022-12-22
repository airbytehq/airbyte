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
import { ConnectionPageRoutePaths } from "./types";

export const ConnectionsRoutes: React.FC = () => (
  <Suspense fallback={<LoadingPage />}>
    <Routes>
      <Route path={RoutePaths.ConnectionNew} element={<CreateConnectionPage />} />
      <Route path={ConnectionPageRoutePaths.ROOT} element={<ConnectionPage />}>
        <Route path={ConnectionPageRoutePaths.STATUS} element={<ConnectionStatusPage />} />
        <Route path={ConnectionPageRoutePaths.REPLICATION} element={<ConnectionReplicationPage />} />
        <Route path={ConnectionPageRoutePaths.TRANSFORMATION} element={<ConnectionTransformationPage />} />
        <Route path={ConnectionPageRoutePaths.SETTINGS} element={<ConnectionSettingsPage />} />
        <Route index element={<Navigate to={ConnectionPageRoutePaths.STATUS} replace />} />
      </Route>
      <Route index element={<AllConnectionsPage />} />
    </Routes>
  </Suspense>
);
