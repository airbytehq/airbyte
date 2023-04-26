import React, { Suspense, useState } from "react";
import { useEffectOnce } from "react-use";
import styled from "styled-components";

import ApiErrorBoundary from "components/ApiErrorBoundary";
import HeadTitle from "components/HeadTitle";
import LoadingPage from "components/LoadingPage";

import { useAnalyticsService, useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useCurrentWorkspaceState } from "services/workspaces/WorkspacesService";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";

import ConnectionStep from "./components/ConnectionStep";
import DestinationStep from "./components/DestinationStep";
import FinalStep from "./components/FinalStep";
import LetterLine from "./components/LetterLine";
import SourceStep from "./components/SourceStep";
import WelcomeStep from "./components/WelcomeStep";
import { StepType } from "./types";
import useGetStepsConfig from "./useStepsConfig";

const Content = styled.div<{ big?: boolean; medium?: boolean }>`
  width: 100%;
  max-width: ${({ big, medium }) => (big ? 1140 : medium ? 730 : 550)}px;
  margin: 0 auto;
  padding: 10px 0 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100%;
  position: relative;
`;

const ScreenContent = styled.div`
  background-color: #2f3177;
  width: 100%;
  position: relative;
`;

const OnboardingPage: React.FC = () => {
  const analyticsService = useAnalyticsService();
  useTrackPage(PageTrackingCodes.ONBOARDING);

  useEffectOnce(() => {
    analyticsService.page("Onboarding Page");
  });

  const { hasConnections, hasDestinations, hasSources } = useCurrentWorkspaceState();

  const [animateExit, setAnimateExit] = useState(false);
  const [hasApiError, setHasApiError] = useState(false);

  const afterUpdateStep = () => {
    setAnimateExit(false);
  };

  const { currentStep, setCurrentStep } = useGetStepsConfig(
    hasSources,
    hasDestinations,
    hasConnections,
    afterUpdateStep
  );

  return (
    <ConnectorDocumentationWrapper>
      <HeadTitle titles={[{ title: "Set First Connection" }]} />
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
          <Suspense fallback={<LoadingPage />}>
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
        </Content>
      </ScreenContent>
    </ConnectorDocumentationWrapper>
  );
};

export default OnboardingPage;
