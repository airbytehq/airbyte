import React, { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useFetcher, useResource } from "rest-hooks";

import PageTitle from "../../../../components/PageTitle";
import StepsMenu from "../../../../components/StepsMenu";
import SourceStep from "./components/SourceStep";
import ConnectionStep from "./components/ConnectionStep";
import { Routes } from "../../../routes";
import useRouter from "../../../../components/hooks/useRouterHook";
import DestinationImplementationResource from "../../../../core/resources/DestinationImplementation";
import config from "../../../../config";
import SourceResource from "../../../../core/resources/Source";
import DestinationResource from "../../../../core/resources/Destination";
import SourceImplementationResource, {
  SourceImplementation
} from "../../../../core/resources/SourceImplementation";
import FrequencyConfig from "../../../../data/FrequencyConfig.json";
import ConnectionResource from "../../../../core/resources/Connection";
import { SyncSchema } from "../../../../core/resources/Schema";
import { AnalyticsService } from "../../../../core/analytics/AnalyticsService";

const Content = styled.div`
  max-width: 638px;
  margin: 13px auto;
`;

export enum StepsTypes {
  CREATE_SOURCE = "select-source",
  SET_UP_CONNECTION = "set-up-connection"
}

const CreateSourcePage: React.FC = () => {
  const { push } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<number>(0);

  const { destinations } = useResource(
    DestinationImplementationResource.listShape(),
    {
      workspaceId: config.ui.workspaceId
    }
  );
  const createConnection = useFetcher(ConnectionResource.createShape());
  const currentDestination = destinations[0]; // Now we have only one destination. If we support multiple destinations we will fix this line
  const { sources } = useResource(SourceResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });
  const destination = useResource(DestinationResource.detailShape(), {
    destinationId: currentDestination.destinationId
  });
  const createSourcesImplementation = useFetcher(
    SourceImplementationResource.createShape()
  );
  const sourcesDropDownData = useMemo(
    () =>
      sources.map(item => ({
        text: item.name,
        value: item.sourceId,
        img: "/default-logo-catalog.svg"
      })),
    [sources]
  );

  const steps = [
    {
      id: StepsTypes.CREATE_SOURCE,
      name: <FormattedMessage id={"sources.selectSource"} />
    },
    {
      id: StepsTypes.SET_UP_CONNECTION,
      name: <FormattedMessage id={"onboarding.setUpConnection"} />
    }
  ];
  const [currentStep, setCurrentStep] = useState(StepsTypes.CREATE_SOURCE);
  const [
    currentSourceImplementation,
    setCurrentSourceImplementation
  ] = useState<SourceImplementation | null>(null);

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    specificationId?: string;
    connectionConfiguration?: any;
  }) => {
    const connector = sources.find(
      item => item.sourceId === values.serviceType
    );
    setErrorStatusRequest(0);
    AnalyticsService.track("New Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Test a connector",
      connector_source: connector?.name,
      connector_source_id: values.serviceType
    });

    try {
      const result = await createSourcesImplementation(
        {},
        {
          name: values.name,
          workspaceId: config.ui.workspaceId,
          sourceSpecificationId: values.specificationId,
          connectionConfiguration: values.connectionConfiguration
        }
      );
      setCurrentSourceImplementation(result);
      setSuccessRequest(true);
      AnalyticsService.track("New Source - Action", {
        user_id: config.ui.workspaceId,
        action: "Tested connector - success",
        connector_source: connector?.name,
        connector_source_id: values.serviceType
      });
      setTimeout(() => {
        setSuccessRequest(false);
        setCurrentStep(StepsTypes.SET_UP_CONNECTION);
      }, 2000);
    } catch (e) {
      AnalyticsService.track("New Source - Action", {
        user_id: config.ui.workspaceId,
        action: "Tested connector - failure",
        connector_source: connector?.name,
        connector_source_id: values.serviceType
      });
      setErrorStatusRequest(e.status);
    }
  };
  const onSubmitConnectionStep = async (values: {
    frequency: string;
    syncSchema: SyncSchema;
  }) => {
    const frequencyData = FrequencyConfig.find(
      item => item.value === values.frequency
    );
    const sourceInfo = sources.find(
      item => item.sourceId === currentSourceImplementation?.sourceId
    );
    setErrorStatusRequest(0);
    try {
      await createConnection(
        {
          sourceId: sourceInfo?.sourceId || "",
          sourceName: sourceInfo?.name || "",
          name: currentSourceImplementation?.name || ""
        },
        {
          sourceImplementationId:
            currentSourceImplementation?.sourceImplementationId,
          destinationImplementationId:
            currentDestination.destinationImplementationId,
          syncMode: "full_refresh",
          schedule: frequencyData?.config,
          status: "active",
          syncSchema: values.syncSchema
        },
        [
          [
            ConnectionResource.listShape(),
            { workspaceId: config.ui.workspaceId },
            (
              newConnectionId: string,
              connectionsIds: { connections: string[] }
            ) => ({
              connections: [
                ...(connectionsIds?.connections || []),
                newConnectionId
              ]
            })
          ]
        ]
      );

      AnalyticsService.track("New Connection - Action", {
        user_id: config.ui.workspaceId,
        action: "Set up connection",
        frequency: frequencyData?.text,
        connector_source: sourceInfo?.name,
        connector_source_id: sourceInfo?.sourceId,
        connector_destination: currentDestination?.name,
        connector_destination_id: currentDestination?.destinationId
      });

      push(Routes.Root);
    } catch (e) {
      setErrorStatusRequest(e.status);
    }
  };
  const renderStep = () => {
    if (currentStep === StepsTypes.CREATE_SOURCE) {
      return (
        <SourceStep
          onSubmit={onSubmitSourceStep}
          dropDownData={sourcesDropDownData}
          destination={destination}
          hasSuccess={successRequest}
          errorStatus={errorStatusRequest}
        />
      );
    }

    return (
      <ConnectionStep
        onSubmit={onSubmitConnectionStep}
        destination={destination}
        sourceId={currentSourceImplementation?.sourceId || ""}
        sourceImplementationId={
          currentSourceImplementation?.sourceImplementationId || ""
        }
      />
    );
  };

  return (
    <>
      <PageTitle
        withLine
        title={<FormattedMessage id="sources.newSourceTitle" />}
        middleComponent={<StepsMenu data={steps} activeStep={currentStep} />}
      />
      <Content>{renderStep()}</Content>
    </>
  );
};

export default CreateSourcePage;
