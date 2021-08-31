import React, { useEffect, useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlay } from "@fortawesome/free-solid-svg-icons";
import { useResource } from "rest-hooks";

import { useConfig } from "config";

import { Link } from "components";
import { H2 } from "components";
import StepsMenu from "components/StepsMenu";
import HeadTitle from "components/HeadTitle";
import Version from "components/Version";

import useSource, { useSourceList } from "hooks/services/useSourceHook";
import useDestination, {
  useDestinationList,
} from "hooks/services/useDestinationHook";
import { JobInfo } from "core/resources/Scheduler";
import { ConnectionConfiguration } from "core/domain/connection";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import useGetStepsConfig from "./useStepsConfig";
import SourceStep from "./components/SourceStep";
import DestinationStep from "./components/DestinationStep";
import ConnectionStep from "./components/ConnectionStep";
import { StepType } from "./types";
import { useAnalytics } from "hooks/useAnalytics";

const Content = styled.div<{ big?: boolean }>`
  width: 100%;
  max-width: ${({ big }) => (big ? 1140 : 813)}px;
  margin: 0 auto;
  padding: 33px 0 13px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  min-height: 100%;
  overflow: hidden;
`;

const Main = styled.div`
  width: 100%;
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

const TutorialLink = styled(Link)`
  margin-top: 32px;
  font-size: 14px;
  text-align: center;
  display: block;
`;

const PlayIcon = styled(FontAwesomeIcon)`
  margin-right: 6px;
`;

const OnboardingPage: React.FC = () => {
  const analyticsService = useAnalytics();
  const config = useConfig();

  useEffect(() => {
    analyticsService.page("Onboarding Page");
  }, []);

  const { sources } = useSourceList();
  const { destinations } = useDestinationList();

  const { sourceDefinitions } = useResource(
    SourceDefinitionResource.listShape(),
    {}
  );
  const { destinationDefinitions } = useResource(
    DestinationDefinitionResource.listShape(),
    {}
  );

  const { createSource, recreateSource } = useSource();
  const { createDestination, recreateDestination } = useDestination();

  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<{
    status: number;
    response: JobInfo;
    message: string;
  } | null>(null);

  const afterUpdateStep = () => {
    setSuccessRequest(false);
    setErrorStatusRequest(null);
  };

  const { currentStep, setCurrentStep, steps } = useGetStepsConfig(
    !!sources.length,
    !!destinations.length,
    afterUpdateStep
  );

  const getSourceDefinitionById = (id: string) =>
    sourceDefinitions.find((item) => item.sourceDefinitionId === id);

  const getDestinationDefinitionById = (id: string) =>
    destinationDefinitions.find((item) => item.destinationDefinitionId === id);

  const renderStep = () => {
    if (currentStep === StepType.CREATE_SOURCE) {
      const onSubmitSourceStep = async (values: {
        name: string;
        serviceType: string;
        sourceId?: string;
        connectionConfiguration?: ConnectionConfiguration;
      }) => {
        setErrorStatusRequest(null);
        const sourceConnector = getSourceDefinitionById(values.serviceType);

        try {
          if (!!sources.length) {
            await recreateSource({
              values,
              sourceId: sources[0].sourceId,
            });
          } else {
            await createSource({ values, sourceConnector });
          }

          setSuccessRequest(true);
          setTimeout(() => {
            setSuccessRequest(false);
            setCurrentStep(StepType.CREATE_DESTINATION);
          }, 2000);
        } catch (e) {
          setErrorStatusRequest(e);
        }
      };
      return (
        <SourceStep
          afterSelectConnector={() => setErrorStatusRequest(null)}
          jobInfo={errorStatusRequest?.response}
          onSubmit={onSubmitSourceStep}
          availableServices={sourceDefinitions}
          hasSuccess={successRequest}
          error={errorStatusRequest}
          // source={sources.length && !successRequest ? sources[0] : undefined}
        />
      );
    }
    if (currentStep === StepType.CREATE_DESTINATION) {
      const onSubmitDestinationStep = async (values: {
        name: string;
        serviceType: string;
        destinationDefinitionId?: string;
        connectionConfiguration?: ConnectionConfiguration;
      }) => {
        setErrorStatusRequest(null);
        const destinationConnector = getDestinationDefinitionById(
          values.serviceType
        );

        try {
          if (!!destinations.length) {
            await recreateDestination({
              values,
              destinationId: destinations[0].destinationId,
            });
          } else {
            await createDestination({
              values,
              destinationConnector,
            });
          }

          setSuccessRequest(true);
          setTimeout(() => {
            setSuccessRequest(false);
            setCurrentStep(StepType.SET_UP_CONNECTION);
          }, 2000);
        } catch (e) {
          setErrorStatusRequest(e);
        }
      };
      return (
        <DestinationStep
          afterSelectConnector={() => setErrorStatusRequest(null)}
          jobInfo={errorStatusRequest?.response}
          onSubmit={onSubmitDestinationStep}
          availableServices={destinationDefinitions}
          hasSuccess={successRequest}
          error={errorStatusRequest}
          currentSourceDefinitionId={sources[0].sourceDefinitionId}
          // destination={
          //   destinations.length && !successRequest ? destinations[0] : undefined
          // }
        />
      );
    }

    return (
      <ConnectionStep
        errorStatus={errorStatusRequest?.status}
        source={sources[0]}
        destination={destinations[0]}
      />
    );
  };

  return (
    <Content big={currentStep === StepType.SET_UP_CONNECTION}>
      <HeadTitle titles={[{ id: "onboarding.headTitle" }]} />
      <Main>
        <Img src="/welcome.svg" height={132} />
        <MainTitle center>
          <FormattedMessage id="onboarding.title" />
        </MainTitle>
        <Subtitle>
          <FormattedMessage id="onboarding.subtitle" />
        </Subtitle>
        <StepsCover>
          <StepsMenu data={steps} activeStep={currentStep} />
        </StepsCover>
        {renderStep()}
        <TutorialLink
          as="a"
          $clear
          target="_blank"
          href={config.ui.tutorialLink}
        >
          <PlayIcon icon={faPlay} />
          <FormattedMessage id="onboarding.tutorial" />
        </TutorialLink>
      </Main>
      <Version />
    </Content>
  );
};

export default OnboardingPage;
