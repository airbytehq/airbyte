import React, { Suspense, useState } from "react";
import { Navigate, Route, Routes, useParams } from "react-router-dom";

import { LoadingPage, MainPageWithScroll } from "components";
import HeadTitle from "components/HeadTitle";

import { getScheduleInfo } from "config/utils";
import { Action, Namespace } from "core/analytics";
import { ConnectionStatus } from "core/request/AirbyteClient";
import { useAnalyticsService, useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useGetConnection } from "hooks/services/useConnectionHook";

import { ConnectionPageTitle } from "./ConnectionPageTitle";
import { ConnectionReplicationTab } from "./ConnectionReplicationTab";
import { ConnectionSettingsRoutes } from "./ConnectionSettingsRoutes";
import { ConnectionSettingsTab } from "./ConnectionSettingsTab";
import { ConnectionStatusTab } from "./ConnectionStatusTab";
import { ConnectionTransformationTab } from "./ConnectionTransformationTab";

export const ConnectionItemPage: React.FC = () => {
  const params = useParams<{
    connectionId: string;
    "*": ConnectionSettingsRoutes;
  }>();
  const connectionId = params.connectionId || "";
  const currentStep = params["*"] || ConnectionSettingsRoutes.STATUS;
  const connection = useGetConnection(connectionId);
  const [isStatusUpdating, setStatusUpdating] = useState(false);
  const analyticsService = useAnalyticsService();

  useTrackPage(PageTrackingCodes.CONNECTIONS_ITEM);
  const { source, destination } = connection;

  const onAfterSaveSchema = () => {
    analyticsService.track(Namespace.CONNECTION, Action.EDIT_SCHEMA, {
      actionDescription: "Connection saved with catalog changes",
      connector_source: source.sourceName,
      connector_source_definition_id: source.sourceDefinitionId,
      connector_destination: destination.destinationName,
      connector_destination_definition_id: destination.destinationDefinitionId,
      frequency: !connection.scheduleData ? "manual" : getScheduleInfo(connection.scheduleData),
    });
  };

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
                source: source.name,
                destination: destination.name,
              },
            },
          ]}
        />
      }
      pageTitle={
        <ConnectionPageTitle
          source={source}
          destination={destination}
          connection={connection}
          currentStep={currentStep}
          onStatusUpdating={setStatusUpdating}
        />
      }
    >
      <Suspense fallback={<LoadingPage />}>
        <Routes>
          <Route
            path={ConnectionSettingsRoutes.STATUS}
            element={<ConnectionStatusTab connection={connection} isStatusUpdating={isStatusUpdating} />}
          />
          <Route
            path={ConnectionSettingsRoutes.REPLICATION}
            element={<ConnectionReplicationTab onAfterSaveSchema={onAfterSaveSchema} connectionId={connectionId} />}
          />
          <Route
            path={ConnectionSettingsRoutes.TRANSFORMATION}
            element={<ConnectionTransformationTab connection={connection} />}
          />
          <Route
            path={ConnectionSettingsRoutes.SETTINGS}
            element={
              isConnectionDeleted ? <Navigate replace to=".." /> : <ConnectionSettingsTab connection={connection} />
            }
          />
          <Route index element={<Navigate to={ConnectionSettingsRoutes.STATUS} replace />} />
        </Routes>
      </Suspense>
    </MainPageWithScroll>
  );
};
