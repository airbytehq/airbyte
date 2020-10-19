import React, { useEffect, useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import { H2 } from "../../components/Titles";
import StepsMenu from "../../components/StepsMenu";
import SourceStep from "./components/SourceStep";
import DestinationStep from "./components/DestinationStep";
import ConnectionStep from "./components/ConnectionStep";
import SourceImplementationResource from "../../core/resources/SourceImplementation";
import DestinationImplementationResource from "../../core/resources/DestinationImplementation";
import config from "../../config";
import StepsConfig, { StepsTypes } from "./components/StepsConfig";
import PrepareDropDownLists from "./components/PrepareDropDownLists";
import { Routes } from "../routes";
import useRouter from "../../components/hooks/useRouterHook";
import { SyncSchema } from "../../core/resources/Schema";
import { AnalyticsService } from "../../core/analytics/AnalyticsService";
import useSource from "../../components/hooks/services/useSourceHook";
import useDestination from "../../components/hooks/services/useDestinationHook";
import useConnection from "../../components/hooks/services/useConnectionHook";

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
  const { createSource, recreateSource } = useSource();
  const { createDestination, recreateDestination } = useDestination();
  const { createConnection } = useConnection();

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

  const afterUpdateStep = () => {
    setSuccessRequest(false);
    setErrorStatusRequest(0);
  };

  const { currentStep, steps, setCurrentStep } = StepsConfig(
    !!sources.length,
    !!destinations.length,
    afterUpdateStep
  );

  const {
    sourcesDropDownData,
    destinationsDropDownData,
    getSourceById,
    getDestinationById
  } = PrepareDropDownLists();

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    sourceId?: string;
    connectionConfiguration?: any;
  }) => {
    setErrorStatusRequest(0);
    const sourceConnector = getSourceById(values.serviceType);

    try {
      if (!!sources.length) {
        await recreateSource({
          values,
          sourceImplementationId: sources[0].sourceImplementationId
        });
      } else {
        await createSource({ values, sourceConnector });
      }

      setSuccessRequest(true);
      setTimeout(() => {
        setSuccessRequest(false);
        setCurrentStep(StepsTypes.CREATE_DESTINATION);
      }, 2000);
    } catch (e) {
      setErrorStatusRequest(e.status);
    }
  };

  const onSubmitDestinationStep = async (values: {
    name: string;
    serviceType: string;
    destinationId?: string;
    connectionConfiguration?: any;
  }) => {
    setErrorStatusRequest(0);
    const destinationConnector = getDestinationById(values.serviceType);

    try {
      if (!!destinations.length) {
        await recreateDestination({
          values,
          destinationImplementationId:
            destinations[0].destinationImplementationId
        });
      } else {
        await createDestination({
          values,
          destinationConnector
        });
      }

      setSuccessRequest(true);
      setTimeout(() => {
        setSuccessRequest(false);
        setCurrentStep(StepsTypes.SET_UP_CONNECTION);
      }, 2000);
    } catch (e) {
      setErrorStatusRequest(e.status);
    }
  };

  const onSubmitConnectionStep = async (values: {
    frequency: string;
    syncSchema: SyncSchema;
    source?: {
      name: string;
      sourceId: string;
    };
  }) => {
    const sourceConnector = getSourceById(sources[0].sourceId);
    const destinationConnector = getDestinationById(
      destinations[0].destinationId
    );

    setErrorStatusRequest(0);
    try {
      await createConnection({
        values,
        sourceImplementation: sources[0],
        destinationImplementationId:
          destinations[0].destinationImplementationId,
        sourceConnector,
        destinationConnector
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
