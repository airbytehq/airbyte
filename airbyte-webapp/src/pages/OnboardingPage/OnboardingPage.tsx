import React, { Suspense, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useEffectOnce } from "react-use";
import styled from "styled-components";

import { Button } from "components";
import ApiErrorBoundary from "components/ApiErrorBoundary";
import HeadTitle from "components/HeadTitle";
import LoadingPage from "components/LoadingPage";

import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import useWorkspace from "hooks/services/useWorkspace";
import useRouterHook from "hooks/useRouter";
import { useCurrentWorkspaceState } from "services/workspaces/WorkspacesService";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";

import { RoutePaths } from "../routePaths";
import ConnectionStep from "./components/ConnectionStep";
import DestinationStep from "./components/DestinationStep";
import FinalStep from "./components/FinalStep";
import HighlightedText from "./components/HighlightedText";
import LetterLine from "./components/LetterLine";
import SourceStep from "./components/SourceStep";
import StepsCounter from "./components/StepsCounter";
import TitlesBlock from "./components/TitlesBlock";
import WelcomeStep from "./components/WelcomeStep";
import { StepType } from "./types";
import useGetStepsConfig from "./useStepsConfig";

const Content = styled.div<{ big?: boolean; medium?: boolean }>`
  width: 100%;
  max-width: ${({ big, medium }) => (big ? 1140 : medium ? 730 : 550)}px;
  margin: 0 auto;
  padding: 75px 0 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100%;
  position: relative;
  z-index: 2;
`;

const Footer = styled.div`
  width: 100%;
  height: 100px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px 0;
`;

const ScreenContent = styled.div`
  width: 100%;
  position: relative;
`;

const TITLE_BY_STEP: Partial<Record<StepType, string>> = {
  [StepType.CREATE_SOURCE]: "FirstSource",
  [StepType.CREATE_DESTINATION]: "FirstDestination",
  [StepType.SET_UP_CONNECTION]: "Connection",
};

const OnboardingPage: React.FC = () => {
  const analyticsService = useAnalyticsService();
  const { push } = useRouterHook();

  useEffectOnce(() => {
    analyticsService.page("Onboarding Page");
  });

  const { finishOnboarding } = useWorkspace();
  const { hasConnections, hasDestinations, hasSources } = useCurrentWorkspaceState();

  const [animateExit, setAnimateExit] = useState(false);
  const [hasApiError, setHasApiError] = useState(false);

  const afterUpdateStep = () => {
    setAnimateExit(false);
  };

  const { currentStep, setCurrentStep, steps } = useGetStepsConfig(
    hasSources,
    hasDestinations,
    hasConnections,
    afterUpdateStep
  );

  const handleFinishOnboarding = () => {
    finishOnboarding(currentStep);
    push(RoutePaths.Connections);
  };

  return (
    <ConnectorDocumentationWrapper>
      <ScreenContent>
        {!hasApiError && (
          <>
            {currentStep === StepType.CREATE_SOURCE ? (
              <LetterLine exit={animateExit} />
            ) : currentStep === StepType.CREATE_DESTINATION ? (
              <LetterLine onRight exit={animateExit} />
            ) : null}
          </>
        )}
        <Content
          big={currentStep === StepType.SET_UP_CONNECTION}
          medium={currentStep === StepType.INSTRUCTION || currentStep === StepType.FINAL}
        >
          <HeadTitle titles={[{ id: "onboarding.headTitle" }]} />
          <StepsCounter steps={steps} currentStep={currentStep} />
          <Suspense fallback={<LoadingPage />}>
            {TITLE_BY_STEP[currentStep] && (
              <TitlesBlock
                title={
                  <FormattedMessage
                    id={`onboarding.create${TITLE_BY_STEP[currentStep]}`}
                    values={{
                      name: (name: React.ReactNode[]) => <HighlightedText>{name}</HighlightedText>,
                    }}
                  />
                }
              >
                <FormattedMessage id={`onboarding.create${TITLE_BY_STEP[currentStep]}.text`} />
              </TitlesBlock>
            )}
            <ApiErrorBoundary
              onError={(error) => {
                setHasApiError(!!error);
              }}
            >
              {currentStep === StepType.INSTRUCTION && (
                <WelcomeStep onNextStep={() => setCurrentStep(StepType.CREATE_SOURCE)} />
              )}
              {currentStep === StepType.CREATE_SOURCE && (
                <SourceStep
                  onSuccess={() => setAnimateExit(true)}
                  onNextStep={() => setCurrentStep(StepType.CREATE_DESTINATION)}
                />
              )}
              {currentStep === StepType.CREATE_DESTINATION && (
                <DestinationStep
                  onSuccess={() => setAnimateExit(true)}
                  onNextStep={() => setCurrentStep(StepType.SET_UP_CONNECTION)}
                />
              )}
              {currentStep === StepType.SET_UP_CONNECTION && (
                <ConnectionStep onNextStep={() => setCurrentStep(StepType.FINAL)} />
              )}
              {currentStep === StepType.FINAL && <FinalStep />}
            </ApiErrorBoundary>
          </Suspense>
          <Footer>
            <Button secondary onClick={() => handleFinishOnboarding()}>
              {currentStep === StepType.FINAL ? (
                <FormattedMessage id="onboarding.closeOnboarding" />
              ) : (
                <FormattedMessage id="onboarding.skipOnboarding" />
              )}
            </Button>
          </Footer>
        </Content>
      </ScreenContent>
    </ConnectorDocumentationWrapper>
  );
};

export default OnboardingPage;
