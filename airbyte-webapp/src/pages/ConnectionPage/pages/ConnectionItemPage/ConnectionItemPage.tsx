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

import { ConnectionPageTitle } from "./ConnectionPageTitle";
import { ConnectionReplicationTab } from "./ConnectionReplicationTab";
import { ConnectionSettingsRoutes } from "./ConnectionSettingsRoutes";
import { ConnectionSettingsTab } from "./ConnectionSettingsTab";
import { ConnectionStatusTab } from "./ConnectionStatusTab";
import { ConnectionTransformationTab } from "./ConnectionTransformationTab";

export const ConnectionItemPageInner: React.FC = () => {
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
          <Route path={ConnectionSettingsRoutes.STATUS} element={<ConnectionStatusTab />} />
          <Route path={ConnectionSettingsRoutes.REPLICATION} element={<ConnectionReplicationTab />} />
          <Route path={ConnectionSettingsRoutes.TRANSFORMATION} element={<ConnectionTransformationTab />} />
          <Route
            path={ConnectionSettingsRoutes.SETTINGS}
            element={isConnectionDeleted ? <Navigate replace to=".." /> : <ConnectionSettingsTab />}
          />
          <Route index element={<Navigate to={ConnectionSettingsRoutes.STATUS} replace />} />
        </Routes>
      </Suspense>
    </MainPageWithScroll>
  );
};

export const ConnectionItemPage = () => {
  const params = useParams<{
    connectionId: string;
  }>();
  const connectionId = params.connectionId || "";
  return (
    <ConnectionEditServiceProvider connectionId={connectionId}>
      <ConnectionItemPageInner />
    </ConnectionEditServiceProvider>
  );
};
