import React, { Suspense } from "react";
import { useResource } from "rest-hooks";
import { Navigate, Route, Routes } from "react-router-dom";

import { LoadingPage, MainPageWithScroll } from "components";
import HeadTitle from "components/HeadTitle";

import useRouter from "hooks/useRouter";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";

import FrequencyConfig from "config/FrequencyConfig.json";

import ConnectionResource from "core/resources/Connection";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import { equal } from "utils/objects";
import ReplicationView from "./components/ReplicationView";

import StatusView from "./components/StatusView";
import TransformationView from "views/Connection/TransformationView";
import SettingsView from "./components/SettingsView";
import ConnectionPageTitle from "./components/ConnectionPageTitle";

export const ConnectionSettingsRoutes = {
  STATUS: "status",
  TRANSFORMATION: "transformation",
  REPLICATION: "replication",
  SETTINGS: "settings",
} as const;

const ConnectionItemPage: React.FC = () => {
  const { params } = useRouter<{ id: string }>();
  const { id } = params;
  const currentStep = params["*"] || "status";
  const connection = useResource(ConnectionResource.detailShape(), {
    connectionId: id,
  });

  const { source, destination } = connection;

  const sourceDefinition = useResource(
    SourceDefinitionResource.detailShape(),
    source
      ? {
          sourceDefinitionId: source.sourceDefinitionId,
        }
      : null
  );

  const destinationDefinition = useResource(
    DestinationDefinitionResource.detailShape(),
    destination
      ? {
          destinationDefinitionId: destination.destinationDefinitionId,
        }
      : null
  );

  const analyticsService = useAnalyticsService();

  const frequency = FrequencyConfig.find((item) =>
    equal(item.config, connection.schedule)
  );

  const onAfterSaveSchema = () => {
    analyticsService.track("Source - Action", {
      action: "Edit schema",
      connector_source: source.sourceName,
      connector_source_id: source.sourceDefinitionId,
      connector_destination: destination.destinationName,
      connector_destination_definition_id: destination.destinationDefinitionId,
      frequency: frequency?.text,
    });
  };

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
          currentStep={currentStep}
        />
      }
    >
      <Suspense fallback={<LoadingPage />}>
        <Routes>
          <Route
            path={ConnectionSettingsRoutes.STATUS}
            element={
              <StatusView
                connection={connection}
                sourceDefinition={sourceDefinition}
                destinationDefinition={destinationDefinition}
                frequencyText={frequency?.text}
              />
            }
          />
          <Route
            path={ConnectionSettingsRoutes.TRANSFORMATION}
            element={<TransformationView />}
          />
          <Route
            path={ConnectionSettingsRoutes.REPLICATION}
            element={
              <ReplicationView
                onAfterSaveSchema={onAfterSaveSchema}
                connectionId={connection.connectionId}
              />
            }
          />
          <Route
            path={ConnectionSettingsRoutes.SETTINGS}
            element={<SettingsView connectionId={connection.connectionId} />}
          />
          <Route
            index
            element={<Navigate to={ConnectionSettingsRoutes.STATUS} />}
          />
        </Routes>
      </Suspense>
    </MainPageWithScroll>
  );
};

export default ConnectionItemPage;
