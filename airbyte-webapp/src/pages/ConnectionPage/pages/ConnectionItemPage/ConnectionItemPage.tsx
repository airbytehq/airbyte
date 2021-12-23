import React, { Suspense } from "react";
import { useResource } from "rest-hooks";
import { Navigate, Route, Routes } from "react-router-dom";

import { RoutePaths } from "pages/routes";
import { Link, LoadingPage, MainPageWithScroll } from "components";
import PageTitle from "components/PageTitle";
import HeadTitle from "components/HeadTitle";
import StepsMenu from "components/StepsMenu";import useRouter from "hooks/useRouter";
import StatusView from "./components/StatusView";
import TransformationView from "./components/TransformationView";
import SettingsView from "./components/SettingsView";
import ConnectionPageTitle from "./components/ConnectionPageTitle";
import ConnectionResource from "core/resources/Connection";
import FrequencyConfig from "config/FrequencyConfig.json";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import { equal } from "utils/objects";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import ReplicationView from "./components/ReplicationView";

const ConnectionItemPage: React.FC = () => {
  const { params, push } = useRouter<{ id: string }>();
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

  const steps = [
    {
      id: "status",
      name: <FormattedMessage id={"sources.status"} />,
    },
    {
      id: "settings",
      name: <FormattedMessage id={"sources.settings"} />,
    },
  ];

  const onSelectStep = (id: string) => {
    if (id === "settings") {
      push(`${RoutePaths.Settings}`);
    } else {
      push("");
    }
  };

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
      <Suspense fallback={<LoadingPage />}>
        <Routes>
          <Route
            index
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
            path="settings"
            element={
              <SettingsView
                onAfterSaveSchema={onAfterSaveSchema}
                connectionId={connection.connectionId}
                sourceDefinition={sourceDefinition}
                destinationDefinition={destinationDefinition}
                frequencyText={frequency?.text}
              />
            }
          />
          <Route index element={<Navigate to="status" />} />
        </Routes>
      </Suspense>
    </MainPageWithScroll>
  );
};

export default ConnectionItemPage;
