import React, { Suspense, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useFetcher, useResource } from "rest-hooks";
import styled from "styled-components";

import PageTitle from "../../../../components/PageTitle";
import Breadcrumbs from "../../../../components/Breadcrumbs";
import useRouter from "../../../../components/hooks/useRouterHook";
import { Routes } from "../../../routes";
import StepsMenu from "../../../../components/StepsMenu";
import StatusView from "./components/StatusView";
import SettingsView from "./components/SettingsView";
import SchemaView from "./components/SchemaView";
import ConnectionResource from "../../../../core/resources/Connection";
import LoadingPage from "../../../../components/LoadingPage";
import DestinationImplementationResource from "../../../../core/resources/DestinationImplementation";
import config from "../../../../config";
import DestinationResource from "../../../../core/resources/Destination";
import { AnalyticsService } from "../../../../core/analytics/AnalyticsService";
import FrequencyConfig from "../../../../data/FrequencyConfig.json";

const Content = styled.div`
  overflow-y: auto;
  height: calc(100% - 67px);
  margin-top: -17px;
  padding-top: 17px;
`;

const Page = styled.div`
  overflow-y: hidden;
  height: 100%;
`;

const SourceItemPage: React.FC = () => {
  const { query, push, history } = useRouter();

  const updateConnection = useFetcher(ConnectionResource.updateShape());

  const connection = useResource(ConnectionResource.detailShape(), {
    // @ts-ignore
    connectionId: query.id
  });

  const { destinations } = useResource(
    DestinationImplementationResource.listShape(),
    {
      workspaceId: config.ui.workspaceId
    }
  );
  const currentDestination = destinations[0]; // Now we have only one destination. If we support multiple destinations we will fix this line
  const destination = useResource(DestinationResource.detailShape(), {
    destinationId: currentDestination.destinationId
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
    },
    {
      id: "settings",
      name: <FormattedMessage id={"sources.settings"} />
    }
  ];
  const [currentStep, setCurrentStep] = useState("status");
  const onSelectStep = (id: string) => setCurrentStep(id);

  const onClickBack = () =>
    history.length > 2 ? history.goBack() : push(Routes.Source);

  const breadcrumbsData = [
    {
      name: <FormattedMessage id="sidebar.sources" />,
      onClick: onClickBack
    },
    { name: connection.source?.name }
  ];

  const onChangeStatus = async () => {
    await updateConnection(
      {},
      {
        connectionId: connection.connectionId,
        syncSchema: connection.syncSchema,
        schedule: connection.schedule,
        status: connection.status === "active" ? "inactive" : "active"
      }
    );

    AnalyticsService.track("Source - Action", {
      user_id: config.ui.workspaceId,
      action:
        connection.status === "active"
          ? "Disable connection"
          : "Reenable connection",
      connector_source: connection.source?.sourceName,
      connector_destination: destination.name,
      frequency: frequency?.text
    });
  };

  const onAfterSaveSchema = () => {
    AnalyticsService.track("Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Edit schema",
      connector_source: connection.source?.sourceName,
      connector_destination: destination.name,
      frequency: frequency?.text
    });
  };

  const onAfterDelete = () => {
    AnalyticsService.track("Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Delete source",
      connector_source: connection.source?.sourceName,
      connector_destination: destination.name,
      frequency: frequency?.text
    });
  };

  const renderStep = () => {
    if (currentStep === "status") {
      return (
        <StatusView
          sourceData={connection}
          onEnabledChange={onChangeStatus}
          destination={destination}
          frequencyText={frequency?.text}
        />
      );
    }
    if (currentStep === "schema") {
      return (
        <SchemaView
          syncSchema={connection.syncSchema}
          connectionId={connection.connectionId}
          connectionStatus={connection.status}
          afterSave={onAfterSaveSchema}
        />
      );
    }

    return <SettingsView sourceData={connection} afterDelete={onAfterDelete} />;
  };

  return (
    <Page>
      <PageTitle
        withLine
        title={<Breadcrumbs data={breadcrumbsData} />}
        middleComponent={
          <StepsMenu
            lightMode
            data={steps}
            onSelect={onSelectStep}
            activeStep={currentStep}
          />
        }
      />
      <Content>
        <Suspense fallback={<LoadingPage />}>{renderStep()}</Suspense>
      </Content>
    </Page>
  );
};

export default SourceItemPage;
