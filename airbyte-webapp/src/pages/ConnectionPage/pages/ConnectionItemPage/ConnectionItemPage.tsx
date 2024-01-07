import React, { Suspense, useEffect, useState } from "react";
import { useQueryClient } from "react-query";
import { Navigate, Route, Routes, useParams } from "react-router-dom";

import { LoadingPage } from "components";
import MessageBox from "components/base/MessageBox";
import HeadTitle from "components/HeadTitle";

import { getFrequencyType } from "config/utils";
import { Action, Namespace } from "core/analytics";
import { ConnectionStatus } from "core/request/AirbyteClient";
import { useAnalyticsService, useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useHealth } from "hooks/services/Health";
import { connectionsKeys, useGetConnection } from "hooks/services/useConnectionHook";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";

import ConnectionPageTitle from "./components/ConnectionPageTitle";
import { ReplicationView } from "./components/ReplicationView";
import SettingsView from "./components/SettingsView";
import StatusView from "./components/StatusView";
import { ConnectionSettingsRoutes } from "./ConnectionSettingsRoutes";

const ConnectionItemPage: React.FC = () => {
  const { push, pathname } = useRouter();
  const { healthData } = useHealth();
  const params = useParams<{
    connectionId: string;
    "*": ConnectionSettingsRoutes;
  }>();

  const connectionId = params.connectionId || "";
  const currentStep = params["*"] || ConnectionSettingsRoutes.STATUS;
  const connection = useGetConnection(connectionId);
  const [isStatusUpdating, setStatusUpdating] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSync, setSyncStatus] = useState<boolean | undefined>(undefined);
  const [disabled, setButtonStatus] = useState<boolean | undefined>(false);
  const [lastSyncTime, setLastSyncTime] = useState<number>();
  const analyticsService = useAnalyticsService();
  const [messageId, setMessageId] = useState<string>("");
  const queryClient = useQueryClient();
  useTrackPage(PageTrackingCodes.CONNECTIONS_ITEM);
  const { source, destination } = connection;

  const onAfterSaveSchema = () => {
    analyticsService.track(Namespace.CONNECTION, Action.EDIT_SCHEMA, {
      actionDescription: "Connection saved with catalog changes",
      connector_source: source.sourceName,
      connector_source_definition_id: source.sourceDefinitionId,
      connector_destination: destination.destinationName,
      connector_destination_definition_id: destination.destinationDefinitionId,
      frequency: getFrequencyType(connection.scheduleData?.basicSchedule),
    });

    onOpenMessageBox("connection.configuration.inprogress");
  };
  const isConnectionDeleted = connection?.status === ConnectionStatus.deprecated;

  const onSync = () => {
    if (!pathname.endsWith("status")) {
      push(`/${RoutePaths.Connections}/${connectionId}/status`);
    }
    setSyncStatus(true);
    setButtonStatus(true);
  };

  const afterSync = (disabled?: boolean) => {
    setButtonStatus(disabled);
    if (!disabled) {
      setSyncStatus(false);
    }
  };

  const getLastSyncTime = (dateTime?: number) => {
    setLastSyncTime(dateTime);
  };

  const onOpenMessageBox = (id: string) => {
    setMessageId(id);
  };

  useEffect(() => {
    // Invalidate queries when the activeTab changes
    if (currentStep === ConnectionSettingsRoutes.CONFIGURATIONS) {
      // Step 2: Set loading to true when starting the data fetch
      setIsLoading(true);

      queryClient
        .invalidateQueries(connectionsKeys.detail(connectionId))
        .then(() => {
          return queryClient.refetchQueries(connectionsKeys.detail(connectionId));
          // Step 3: Set loading to false when data fetch is complete
        })
        .then(() => {
          setIsLoading(false);
        })
        .catch((error) => {
          console.error("Error fetching data:", error);
          // Handle error here and possibly show an error message
          setIsLoading(false); // Ensure loading is set to false even in case of an error
        });
    }
  }, [currentStep]);

  return (
    <>
      {isLoading && currentStep === ConnectionSettingsRoutes.CONFIGURATIONS ? (
        <LoadingPage />
      ) : (
        <>
          <MessageBox
            message={messageId}
            onClose={() => setMessageId("")}
            type={messageId === "connection.configuration.inprogress" ? "error" : "info"}
            position="center"
          />
          <HeadTitle
            titles={[
              { id: "connection.pageTitle" },
              {
                id: "connection.fromTo",
                values: {
                  source: source.name,
                  destination: destination.name,
                },
              },
            ]}
          />
          <ConnectionPageTitle
            source={source}
            destination={destination}
            connection={connection}
            currentStep={currentStep}
            onStatusUpdating={setStatusUpdating}
            onSync={onSync}
            disabled={disabled}
            lastSyncTime={lastSyncTime}
          />
          <Suspense fallback={<LoadingPage />}>
            <Routes>
              <Route
                path={ConnectionSettingsRoutes.STATUS}
                element={
                  <StatusView
                    onOpenMessageBox={onOpenMessageBox}
                    connection={connection}
                    isStatusUpdating={isStatusUpdating}
                    isSync={isSync}
                    afterSync={afterSync}
                    getLastSyncTime={getLastSyncTime}
                  />
                }
              />
              <Route
                path={ConnectionSettingsRoutes.CONFIGURATIONS}
                element={
                  <ReplicationView
                    onAfterSaveSchema={onAfterSaveSchema}
                    connectionId={connectionId}
                    healthData={healthData}
                  />
                }
              />
              <Route
                path={ConnectionSettingsRoutes.DANGERZONE}
                element={isConnectionDeleted ? <Navigate replace to=".." /> : <SettingsView connection={connection} />}
              />
              <Route index element={<Navigate to={ConnectionSettingsRoutes.STATUS} replace />} />
            </Routes>
          </Suspense>
        </>
      )}
    </>
  );
};

export default ConnectionItemPage;
