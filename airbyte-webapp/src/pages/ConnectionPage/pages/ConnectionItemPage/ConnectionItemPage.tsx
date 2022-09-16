import React, { Suspense, useState } from "react";
import { Navigate, Route, Routes, useParams } from "react-router-dom";

import { LoadingPage, MainPageWithScroll } from "components";
import HeadTitle from "components/HeadTitle";

import { ConnectionStatus } from "core/request/AirbyteClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { ConnectionFormServiceProvider } from "hooks/services/Connection/ConnectionFormService";
import { useUniqueFormId } from "hooks/services/FormChangeTracker";
import { useConnectionLoad } from "hooks/services/useConnectionHook";
import TransformationView from "pages/ConnectionPage/pages/ConnectionItemPage/components/TransformationView";

import { ConnectionPageTitle } from "./components/ConnectionPageTitle";
import { ConnectionReplication } from "./components/ConnectionReplication";
import SettingsView from "./components/SettingsView";
import StatusView from "./components/StatusView";
import { ConnectionSettingsRoutes } from "./ConnectionSettingsRoutes";

export const ConnectionItemPage: React.FC = () => {
  const params = useParams<{
    connectionId: string;
  }>();
  const connectionId = params.connectionId || "";
  const { connection, schemaHasBeenRefreshed, setConnection, setSchemaHasBeenRefreshed, refreshConnectionCatalog } =
    useConnectionLoad(connectionId);
  const [isStatusUpdating, setStatusUpdating] = useState(false);

  useTrackPage(PageTrackingCodes.CONNECTIONS_ITEM);

  const isConnectionDeleted = connection.status === ConnectionStatus.deprecated;

  return (
    <ConnectionFormServiceProvider
      connection={connection}
      setConnection={setConnection}
      refreshCatalog={refreshConnectionCatalog}
      schemaHasBeenRefreshed={schemaHasBeenRefreshed}
      setSchemaHasBeenRefreshed={setSchemaHasBeenRefreshed}
      mode={connection?.status !== ConnectionStatus.deprecated ? "edit" : "readonly"}
      formId={useUniqueFormId()}
    >
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
    </ConnectionFormServiceProvider>
  );
};
