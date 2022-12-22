import React, { Suspense } from "react";
import { Navigate, Route, Routes, useParams } from "react-router-dom";

import { LoadingPage, MainPageWithScroll } from "components";
import { HeadTitle } from "components/common/HeadTitle";

import { ConnectionStatus } from "core/request/AirbyteClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import {
  ConnectionEditServiceProvider,
  useConnectionEditService,
} from "hooks/services/ConnectionEdit/ConnectionEditService";

import { ConnectionReplicationPage } from "../ConnectionReplicationPage";
import { ConnectionItemSettingsPage } from "../ConnectionSettingsPage";
import { ConnectionStatusPage } from "../ConnectionStatusPage";
import { ConnectionItemTransformationPage } from "../ConnectionTransformationPage";
import { ConnectionPageTitle } from "./ConnectionPageTitle";
import { ConnectionSettingsRoutes } from "./ConnectionSettingsRoutes";

export const ConnectionPageInner: React.FC = () => {
  const { connection } = useConnectionEditService();

  useTrackPage(PageTrackingCodes.CONNECTIONS_ITEM);

  const isConnectionDeleted = connection.status === ConnectionStatus.deprecated;

  return (
    <MainPageWithScroll
      headTitle={
        <HeadTitle
          titles={[
            { id: "sidebar.connections" },
            {
              id: "connection.fromTo",
              values: {
                source: connection.source.name,
                destination: connection.destination.name,
              },
            },
          ]}
        />
      }
      pageTitle={<ConnectionPageTitle />}
    >
      <Suspense fallback={<LoadingPage />}>
        <Routes>
          <Route path={ConnectionSettingsRoutes.STATUS} element={<ConnectionStatusPage />} />
          <Route path={ConnectionSettingsRoutes.REPLICATION} element={<ConnectionReplicationPage />} />
          <Route path={ConnectionSettingsRoutes.TRANSFORMATION} element={<ConnectionItemTransformationPage />} />
          <Route
            path={ConnectionSettingsRoutes.SETTINGS}
            element={isConnectionDeleted ? <Navigate replace to=".." /> : <ConnectionItemSettingsPage />}
          />
          <Route index element={<Navigate to={ConnectionSettingsRoutes.STATUS} replace />} />
        </Routes>
      </Suspense>
    </MainPageWithScroll>
  );
};

export const ConnectionPage = () => {
  const params = useParams<{
    connectionId: string;
  }>();
  const connectionId = params.connectionId || "";
  return (
    <ConnectionEditServiceProvider connectionId={connectionId}>
      <ConnectionPageInner />
    </ConnectionEditServiceProvider>
  );
};
