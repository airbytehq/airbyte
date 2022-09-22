import React, { Suspense, useState } from "react";
import { Navigate, Route, Routes, useParams } from "react-router-dom";

import { LoadingPage, MainPageWithScroll } from "components";
import HeadTitle from "components/HeadTitle";

import { ConnectionStatus } from "core/request/AirbyteClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import {
  ConnectionEditServiceProvider,
  useConnectionEditService,
} from "hooks/services/ConnectionEdit/ConnectionEditService";
import TransformationView from "pages/ConnectionPage/pages/ConnectionItemPage/components/TransformationView";

import { ConnectionPageTitle } from "./components/ConnectionPageTitle";
import { ConnectionReplication } from "./components/ConnectionReplication";
import SettingsView from "./components/SettingsView";
import StatusView from "./components/StatusView";
import { ConnectionSettingsRoutes } from "./ConnectionSettingsRoutes";

export const ConnectionItemPageInner: React.FC = () => {
  const { connection } = useConnectionEditService();
  const [isStatusUpdating, setStatusUpdating] = useState(false);

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
      pageTitle={<ConnectionPageTitle onStatusUpdating={setStatusUpdating} />}
    >
      <Suspense fallback={<LoadingPage />}>
        <Routes>
          <Route
            path={ConnectionSettingsRoutes.STATUS}
            element={<StatusView connection={connection} isStatusUpdating={isStatusUpdating} />}
          />
          <Route path={ConnectionSettingsRoutes.REPLICATION} element={<ConnectionReplication />} />
          <Route
            path={ConnectionSettingsRoutes.TRANSFORMATION}
            element={<TransformationView connection={connection} />}
          />
          <Route
            path={ConnectionSettingsRoutes.SETTINGS}
            element={isConnectionDeleted ? <Navigate replace to=".." /> : <SettingsView connection={connection} />}
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
