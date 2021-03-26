import React, { Suspense, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import PageTitle from "components/PageTitle";
import useRouter from "components/hooks/useRouterHook";
import StepsMenu from "components/StepsMenu";
import StatusView from "./components/StatusView";
import SettingsView from "./components/SettingsView";
import ConnectionResource from "core/resources/Connection";
import LoadingPage from "components/LoadingPage";
import MainPageWithScroll from "components/MainPageWithScroll";
import config from "config";
import { AnalyticsService } from "core/analytics/AnalyticsService";
import FrequencyConfig from "data/FrequencyConfig.json";
import Link from "components/Link";
import { Routes } from "../../../routes";

const ConnectionItemPage: React.FC = () => {
  const { query } = useRouter<{ id: string }>();

  const connection = useResource(ConnectionResource.detailShape(), {
    connectionId: query.id,
  });

  const frequency = FrequencyConfig.find(
    (item) =>
      JSON.stringify(item.config) === JSON.stringify(connection.schedule)
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
  const [currentStep, setCurrentStep] = useState("status");
  const onSelectStep = (id: string) => setCurrentStep(id);

  const onAfterSaveSchema = () => {
    AnalyticsService.track("Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Edit schema",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.destinationName,
      connector_destination_definition_id:
        connection.destination?.destinationDefinitionId,
      frequency: frequency?.text,
    });
  };

  const renderStep = () => {
    if (currentStep === "status") {
      return (
        <StatusView connection={connection} frequencyText={frequency?.text} />
      );
    }

    return (
      <SettingsView
        onAfterSaveSchema={onAfterSaveSchema}
        connectionId={connection.connectionId}
        frequencyText={frequency?.text}
      />
    );
  };

  const linkToSource = () => (
    <Link clear to={`${Routes.Source}/${connection.source?.sourceId}`}>
      {connection.source?.name}
    </Link>
  );

  const linkToDestination = () => (
    <Link
      clear
      to={`${Routes.Destination}/${connection.destination?.destinationId}`}
    >
      {connection.destination?.name}
    </Link>
  );

  return (
    <MainPageWithScroll
      title={
        <PageTitle
          withLine
          title={
            <FormattedMessage
              id="connection.fromTo"
              values={{
                source: linkToSource(),
                destination: linkToDestination(),
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

export default ConnectionItemPage;
