import React, { useEffect, useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { useFetcher, useResource } from "rest-hooks";

import { H2 } from "../../components/Titles";
import StepsMenu from "../../components/StepsMenu";
import SourceStep from "./components/SourceStep";
import DestinationStep from "./components/DestinationStep";
import ConnectionStep from "./components/ConnectionStep";
import SourceImplementationResource from "../../core/resources/SourceImplementation";
import DestinationImplementationResource from "../../core/resources/DestinationImplementation";
import ConnectionResource from "../../core/resources/Connection";
import config from "../../config";
import StepsConfig, { StepsTypes } from "./components/StepsConfig";
import PrepareDropDownLists from "./components/PrepareDropDownLists";
import FrequencyConfig from "../../data/FrequencyConfig.json";
import { Routes } from "../routes";
import useRouter from "../../components/hooks/useRouterHook";
import { Source } from "../../core/resources/Source";
import { SyncSchema } from "../../core/resources/Schema";
import { AnalyticsService } from "../../core/analytics/AnalyticsService";
import WorkspaceResource from "../../core/resources/Workspace";

const Content = styled.div`
  width: 100%;
  max-width: 638px;
  margin: 0 auto;
  padding: 33px 0;
`;

const Img = styled.img`
  text-align: center;
  width: 100%;
`;

const MainTitle = styled(H2)`
  margin-top: -39px;
  font-family: ${({ theme }) => theme.highlightFont};
  color: ${({ theme }) => theme.darkPrimaryColor};
  letter-spacing: 0.008em;
  font-weight: bold;
`;

const Subtitle = styled.div`
  font-size: 14px;
  line-height: 21px;
  color: ${({ theme }) => theme.greyColor40};
  text-align: center;
  margin-top: 7px;
`;

const StepsCover = styled.div`
  margin: 33px 0 28px;
`;

const OnboardingPage: React.FC = () => {
  useEffect(() => {
    AnalyticsService.page("Onboarding Page");
  }, []);

  const { push } = useRouter();

  const { sources } = useResource(SourceImplementationResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });
  const { destinations } = useResource(
    DestinationImplementationResource.listShape(),
    {
      workspaceId: config.ui.workspaceId
    }
  );

  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<number>(0);
  const { currentStep, steps, setCurrentStep } = StepsConfig(
    !!sources.length,
    !!destinations.length
  );
  const createSourcesImplementation = useFetcher(
    SourceImplementationResource.createShape()
  );
  const createDestinationsImplementation = useFetcher(
    DestinationImplementationResource.createShape()
  );
  const createConnection = useFetcher(ConnectionResource.createShape());
  const updateWorkspace = useFetcher(WorkspaceResource.updateShape());
  const workspace = useResource(WorkspaceResource.detailShape(), {
    workspaceId: config.ui.workspaceId
  });

  const {
    sourcesDropDownData,
    destinationsDropDownData,
    getSourceById,
    getDestinationById
  } = PrepareDropDownLists();

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    specificationId?: string;
    connectionConfiguration?: any;
  }) => {
    setErrorStatusRequest(0);

    const sourceConnector = getSourceById(values.serviceType);
    AnalyticsService.track("New Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Test a connector",
      connector_source: sourceConnector?.name,
      connector_source_id: sourceConnector?.sourceId
    });

    try {
      await createSourcesImplementation(
        {},
        {
          name: values.name,
          workspaceId: config.ui.workspaceId,
          sourceSpecificationId: values.specificationId,
          connectionConfiguration: values.connectionConfiguration
        },
        [
          [
            SourceImplementationResource.listShape(),
            { workspaceId: config.ui.workspaceId },
            (
              newSourceImplementationId: string,
              sourcesImplementationIds: { sources: string[] }
            ) => ({
              sources: [
                ...sourcesImplementationIds.sources,
                newSourceImplementationId
              ]
            })
          ]
        ]
      );

      setSuccessRequest(true);
      AnalyticsService.track("New Source - Action", {
        user_id: config.ui.workspaceId,
        action: "Tested connector - success",
        connector_source: sourceConnector?.name,
        connector_source_id: sourceConnector?.sourceId
      });
      setTimeout(() => {
        setSuccessRequest(false);
        setCurrentStep(StepsTypes.CREATE_DESTINATION);
      }, 2000);
    } catch (e) {
      AnalyticsService.track("New Source - Action", {
        user_id: config.ui.workspaceId,
        action: "Tested connector - failure",
        connector_source: sourceConnector?.name,
        connector_source_id: sourceConnector?.sourceId
      });
      setErrorStatusRequest(e.status);
    }
  };

  const onSubmitDestinationStep = async (values: {
    name: string;
    serviceType: string;
    specificationId?: string;
    connectionConfiguration?: any;
  }) => {
    setErrorStatusRequest(0);

    const destinationConnector = getDestinationById(values.serviceType);
    AnalyticsService.track("New Destination - Action", {
      user_id: config.ui.workspaceId,
      action: "Test a connector",
      connector_destination: destinationConnector?.name,
      connector_destination_id: destinationConnector?.destinationId
    });

    try {
      await createDestinationsImplementation(
        {},
        {
          name: values.name,
          workspaceId: config.ui.workspaceId,
          destinationSpecificationId: values.specificationId,
          connectionConfiguration: values.connectionConfiguration
        },
        [
          [
            DestinationImplementationResource.listShape(),
            { workspaceId: config.ui.workspaceId },
            (
              newDestinationImplementationId: string,
              destinationsImplementationIds: { destinations: string[] }
            ) => ({
              destinations: [
                ...destinationsImplementationIds.destinations,
                newDestinationImplementationId
              ]
            })
          ]
        ]
      );

      setSuccessRequest(true);
      AnalyticsService.track("New Destination - Action", {
        user_id: config.ui.workspaceId,
        action: "Tested connector - success",
        connector_destination: destinationConnector?.name,
        connector_destination_id: destinationConnector?.destinationId
      });
      setTimeout(() => {
        setSuccessRequest(false);
        setCurrentStep(StepsTypes.SET_UP_CONNECTION);
      }, 2000);
    } catch (e) {
      AnalyticsService.track("New Destination - Action", {
        user_id: config.ui.workspaceId,
        action: "Tested connector - failure",
        connector_destination: destinationConnector?.name,
        connector_destination_id: destinationConnector?.destinationId
      });
      setErrorStatusRequest(e.status);
    }
  };

  const onSubmitConnectionStep = async (values: {
    frequency: string;
    syncSchema: SyncSchema;
    source?: Source;
  }) => {
    const frequencyData = FrequencyConfig.find(
      item => item.value === values.frequency
    );
    const sourceConnector = getSourceById(sources[0].sourceId);
    const destinationConnector = getDestinationById(
      destinations[0].destinationId
    );

    setErrorStatusRequest(0);
    try {
      await createConnection(
        {
          sourceId: values.source?.sourceId || "",
          sourceName: values.source?.name || "",
          name: sources[0].name || ""
        },
        {
          sourceImplementationId: sources[0].sourceImplementationId,
          destinationImplementationId:
            destinations[0].destinationImplementationId,
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
        connector_source: sourceConnector?.name,
        connector_source_id: sourceConnector?.sourceId,
        connector_destination: destinationConnector?.name,
        connector_destination_id: destinationConnector?.destinationId
      });

      await updateWorkspace(
        {},
        {
          workspaceId: workspace.workspaceId,
          initialSetupComplete: workspace.initialSetupComplete,
          onboardingComplete: true,
          anonymousDataCollection: workspace.anonymousDataCollection,
          news: workspace.news,
          securityUpdates: workspace.securityUpdates
        }
      );

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
          hasSuccess={successRequest}
          errorStatus={errorStatusRequest}
          sourceImplementation={
            sources.length && !successRequest ? sources[0] : undefined
          }
        />
      );
    }
    if (currentStep === StepsTypes.CREATE_DESTINATION) {
      return (
        <DestinationStep
          onSubmit={onSubmitDestinationStep}
          dropDownData={destinationsDropDownData}
          hasSuccess={successRequest}
          errorStatus={errorStatusRequest}
          currentSourceId={sources[0].sourceId}
          destinationImplementation={
            destinations.length && !successRequest ? destinations[0] : undefined
          }
        />
      );
    }

    return (
      <ConnectionStep
        onSubmit={onSubmitConnectionStep}
        currentSourceId={sources[0].sourceId}
        currentDestinationId={destinations[0].destinationId}
        errorStatus={errorStatusRequest}
        sourceImplementationId={sources[0].sourceImplementationId}
      />
    );
  };

  return (
    <Content>
      <Img src="/welcome.svg" height={132} />
      <MainTitle center>
        <FormattedMessage id={"onboarding.title"} />
      </MainTitle>
      <Subtitle>
        <FormattedMessage id={"onboarding.subtitle"} />
      </Subtitle>
      <StepsCover>
        <StepsMenu data={steps} activeStep={currentStep} />
      </StepsCover>
      {renderStep()}
    </Content>
  );
};

export default OnboardingPage;
