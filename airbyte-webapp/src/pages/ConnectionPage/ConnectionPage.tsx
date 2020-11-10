import React, { Suspense, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import PageTitle from "../../components/PageTitle";
import useRouter from "../../components/hooks/useRouterHook";
import StepsMenu from "../../components/StepsMenu";
import StatusView from "./components/StatusView";
import SettingsView from "./components/SettingsView";
import SchemaView from "./components/SchemaView";
import ConnectionResource from "../../core/resources/Connection";
import LoadingPage from "../../components/LoadingPage";
import MainPageWithScroll from "../../components/MainPageWithScroll";
import config from "../../config";
import { AnalyticsService } from "../../core/analytics/AnalyticsService";
import FrequencyConfig from "../..//data/FrequencyConfig.json";
import useConnection from "../../components/hooks/services/useConnectionHook";
import Link from "../../components/Link";
import { Routes } from "../routes";

const ConnectionPage: React.FC = () => {
  const { query } = useRouter();

  const { updateConnection } = useConnection();

  const connection = useResource(ConnectionResource.detailShape(), {
    // @ts-ignore
    connectionId: query.id
  });

  const frequency = FrequencyConfig.find(
    item => JSON.stringify(item.config) === JSON.stringify(connection.schedule)
  );

  const steps = [
    {
      id: "status",
      name: <FormattedMessage id={"sources.status"} />
    },
    {
      id: "schema",
      name: <FormattedMessage id={"sources.schema"} />
    }
    // {
    //   id: "settings",
    //   name: <FormattedMessage id={"sources.settings"} />
    // }
  ];
  const [currentStep, setCurrentStep] = useState("status");
  const onSelectStep = (id: string) => setCurrentStep(id);

  const onChangeStatus = async () => {
    await updateConnection({
      connectionId: connection.connectionId,
      syncSchema: connection.syncSchema,
      schedule: connection.schedule,
      status: connection.status === "active" ? "inactive" : "active"
    });

    AnalyticsService.track("Source - Action", {
      user_id: config.ui.workspaceId,
      action:
        connection.status === "active"
          ? "Disable connection"
          : "Reenable connection",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.name,
      connector_destination_definition_id:
        connection.destination?.destinationDefinitionId,
      frequency: frequency?.text
    });
  };

  const onAfterSaveSchema = () => {
    AnalyticsService.track("Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Edit schema",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.name,
      connector_destination_definition_id:
        connection.destination?.destinationDefinitionId,
      frequency: frequency?.text
    });
  };

  const onAfterDelete = () => {
    AnalyticsService.track("Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Delete source",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.name,
      connector_destination_definition_id:
        connection.destination?.destinationDefinitionId,
      frequency: frequency?.text
    });
  };

  const renderStep = () => {
    if (currentStep === "status") {
      return (
        <StatusView
          connection={connection}
          onEnabledChange={onChangeStatus}
          frequencyText={frequency?.text}
        />
      );
    }
    if (currentStep === "schema") {
      return (
        <SchemaView connection={connection} afterSave={onAfterSaveSchema} />
      );
    }

    return <SettingsView sourceData={connection} afterDelete={onAfterDelete} />;
  };

  return (
    <MainPageWithScroll
      title={
        <PageTitle
          withLine
          title={
            <FormattedMessage
              id="connection.fromTo"
              values={{
                source: (
                  <Link
                    clear
                    to={`${Routes.Source}/${connection.source?.sourceId}`}
                  >
                    {connection.source?.name}
                  </Link>
                ),
                destination: (
                  <Link
                    clear
                    to={`${Routes.Destination}/${connection.destination?.destinationId}`}
                  >
                    {connection.destination?.name}
                  </Link>
                )
              }}
            />
          }
          middleComponent={
            <StepsMenu
              lightMode
              data={steps}
              onSelect={onSelectStep}
              activeStep={currentStep}
            />
          }
        />
      }
    >
      <Suspense fallback={<LoadingPage />}>{renderStep()}</Suspense>
    </MainPageWithScroll>
  );
};

export default ConnectionPage;
