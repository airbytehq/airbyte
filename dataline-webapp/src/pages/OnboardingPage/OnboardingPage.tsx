import React, { useMemo, useState } from "react";
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
import useRouter from "../../components/hooks/useRouterHook";
import { Routes } from "../routes";
import SourceResource from "../../core/resources/Source";
import DestinationResource from "../../core/resources/Destination";
import SourceImplementationResource from "../../core/resources/SourceImplementation";
import DestinationImplementationResource from "../../core/resources/DestinationImplementation";
import config from "../../config";

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
  const { sources } = useResource(SourceImplementationResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });
  const { destinations } = useResource(
    DestinationImplementationResource.listShape(),
    {
      workspaceId: config.ui.workspaceId
    }
  );
  const destinationsImplementation = useResource(
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

  const {
    sourcesDropDownData,
    destinationsDropDownData
  } = PrepareDropDownLists();

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    specificationId?: string;
    connectionConfiguration?: any;
  }) => {
    setErrorStatusRequest(0);
    try {
      await createSourcesImplementation(
        {},
        {
          workspaceId: config.ui.workspaceId,
          sourceSpecificationId: values.specificationId,
          connectionConfiguration: values.connectionConfiguration
        }
      );

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
    specificationId?: string;
    connectionConfiguration?: any;
  }) => {
    setErrorStatusRequest(0);
    try {
      await createDestinationsImplementation(
        {},
        {
          workspaceId: config.ui.workspaceId,
          destinationSpecificationId: values.specificationId,
          connectionConfiguration: values.connectionConfiguration
        }
      );

      setSuccessRequest(true);
      setTimeout(() => {
        setSuccessRequest(false);
        setCurrentStep(StepsTypes.SET_UP_CONNECTION);
      }, 2000);
    } catch (e) {
      setErrorStatusRequest(e.status);
    }
  };

  const onSubmitConnectionStep = async (values: { frequency: string }) => {
    const frequencyData = FrequencyConfig.find(
      item => item.value === values.frequency
    );
    const result = await createConnection(
      {},
      {
        sourceImplementationId: sources[0].sourceImplementationId,
        destinationImplementationId:
          destinations[0].destinationImplementationId,
        syncMode: "full_refresh",
        schedule: frequencyData?.config,
        status: "active"
      }
    );

    console.log(result);
  };

  const renderStep = () => {
    if (currentStep === StepsTypes.CREATE_SOURCE) {
      return (
        <SourceStep
          onSubmit={onSubmitSourceStep}
          dropDownData={sourcesDropDownData}
          hasSuccess={successRequest}
          errorStatus={errorStatusRequest}
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
        />
      );
    }

    return <ConnectionStep onSubmit={onSubmitConnectionStep} />;
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
