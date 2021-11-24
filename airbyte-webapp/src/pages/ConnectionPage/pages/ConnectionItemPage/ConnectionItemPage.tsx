import React, { Suspense } from "react";
import { useResource } from "rest-hooks";

import HeadTitle from "components/HeadTitle";
import useRouter from "hooks/useRouter";
import StatusView from "./components/StatusView";
import TransformationView from "./components/TransformationView";
import SettingsView from "./components/SettingsView";
import ConnectionPageTitle from "./components/ConnectionPageTitle";
import ConnectionResource from "core/resources/Connection";
import LoadingPage from "components/LoadingPage";
import MainPageWithScroll from "components/MainPageWithScroll";
import FrequencyConfig from "config/FrequencyConfig.json";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import { equal } from "utils/objects";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import ReplicationView from "./components/ReplicationView";

type ConnectionItemPageProps = {
  currentStep: "status" | "settings" | "replication" | "transformation";
};

const ConnectionItemPage: React.FC<ConnectionItemPageProps> = ({
  currentStep,
}) => {
  const { query } = useRouter<{ id: string }>();

  const analyticsService = useAnalyticsService();
  const connection = useResource(ConnectionResource.detailShape(), {
    connectionId: query.id,
  });

  const frequency = FrequencyConfig.find((item) =>
    equal(item.config, connection.schedule)
  );

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

  const renderStep = () => {
    if (currentStep === "status") {
      return (
        <StatusView
          connection={connection}
          frequencyText={frequency?.text}
          sourceDefinition={sourceDefinition}
          destinationDefinition={destinationDefinition}
        />
      );
    }
    if (currentStep === "replication") {
      return (
        <ReplicationView
          onAfterSaveSchema={onAfterSaveSchema}
          connectionId={connection.connectionId}
        />
      );
    }
    if (currentStep === "transformation") {
      return <TransformationView />;
    }

    return <SettingsView connectionId={connection.connectionId} />;
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
          connectionId={connection.connectionId}
        />
      }
    >
      <Suspense fallback={<LoadingPage />}>{renderStep()}</Suspense>
    </MainPageWithScroll>
  );
};

export default ConnectionItemPage;
