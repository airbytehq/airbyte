import React, { Suspense, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useEffectOnce } from "react-use";
import styled from "styled-components";

import { Button } from "components";
import HeadTitle from "components/HeadTitle";
import LoadingPage from "components/LoadingPage";

import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import useWorkspace from "hooks/services/useWorkspace";
import useRouterHook from "hooks/useRouter";
import { useCurrentWorkspaceState } from "services/workspaces/WorkspacesService";

import { RoutePaths } from "../routePaths";
import ConnectionStep from "./components/ConnectionStep";
import DestinationStep from "./components/DestinationStep";
import FinalStep from "./components/FinalStep";
import LetterLine from "./components/LetterLine";
import SourceStep from "./components/SourceStep";
import StepsCounter from "./components/StepsCounter";
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

const OnboardingPage: React.FC = () => {
  const analyticsService = useAnalyticsService();
  const { push } = useRouterHook();

  useEffectOnce(() => {
    analyticsService.page("Onboarding Page");
  });

  const { finishOnboarding } = useWorkspace();
  const { hasConnections, hasDestinations, hasSources } = useCurrentWorkspaceState();

  const [animateExit, setAnimateExit] = useState(false);

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
    finishOnboarding();
    push(RoutePaths.Connections);
  };

  return (
    <ScreenContent>
      {currentStep === StepType.CREATE_SOURCE ? (
        <LetterLine exit={animateExit} />
      ) : currentStep === StepType.CREATE_DESTINATION ? (
        <LetterLine onRight exit={animateExit} />
      ) : null}
      <Content
        big={currentStep === StepType.SET_UP_CONNECTION}
        medium={currentStep === StepType.INSTRUCTION || currentStep === StepType.FINAl}
      >
        <HeadTitle titles={[{ id: "onboarding.headTitle" }]} />
        <StepsCounter steps={steps} currentStep={currentStep} />

        <Suspense fallback={<LoadingPage />}>
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
            <ConnectionStep onNextStep={() => setCurrentStep(StepType.FINAl)} />
          )}
          {currentStep === StepType.FINAl && <FinalStep />}
        </Suspense>

        <Footer>
          <Button secondary onClick={() => handleFinishOnboarding()}>
            {currentStep === StepType.FINAl ? (
              <FormattedMessage id="onboarding.closeOnboarding" />
            ) : (
              <FormattedMessage id="onboarding.skipOnboarding" />
            )}
          </Button>
        </Footer>
      </Content>
    </ScreenContent>
  );
};

export default OnboardingPage;
