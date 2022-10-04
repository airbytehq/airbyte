import { useMemo, useState, useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { useLocation } from "react-router-dom";

import { ILocationState, StepType } from "./types";

const useStepsConfig = (
  hasSources: boolean,
  hasDestinations: boolean,
  hasConnections: boolean,
  afterUpdateStep?: () => void
): {
  currentStep: StepType;
  setCurrentStep: (step: StepType) => void;
  steps: Array<{ name: JSX.Element; id: StepType }>;
} => {
  // exp-speedy-connection
  const location = useLocation() as unknown as ILocationState<{ step: StepType }>;

  const getInitialStep = () => {
    // exp-speedy-connection
    if (location.state?.step) {
      return location.state.step;
    }
    if (hasSources) {
      if (hasDestinations) {
        if (hasConnections) {
          return StepType.FINAL;
        }
        return StepType.SET_UP_CONNECTION;
      }
      return StepType.CREATE_DESTINATION;
    }
    return StepType.INSTRUCTION;
  };

  const [currentStep, setCurrentStep] = useState<StepType>(getInitialStep);
  const updateStep = useCallback(
    (step: StepType) => {
      setCurrentStep(step);
      afterUpdateStep?.();
    },
    [setCurrentStep, afterUpdateStep]
  );

  const steps = useMemo(
    () => [
      {
        id: StepType.INSTRUCTION,
        name: <FormattedMessage id="onboarding.instruction" />,
      },
      {
        id: StepType.CREATE_SOURCE,
        name: <FormattedMessage id="onboarding.createSource" />,
        // don't navigate by steps for now
        // onSelect: hasSources
        //   ? () => updateStep(StepType.CREATE_SOURCE)
        //   : undefined
      },
      {
        id: StepType.CREATE_DESTINATION,
        name: <FormattedMessage id="onboarding.createDestination" />,
        // don't navigate by steps for now
        // onSelect:
        //   hasSources || hasDestinations
        //     ? () => updateStep(StepType.CREATE_DESTINATION)
        //     : undefined
      },
      {
        id: StepType.SET_UP_CONNECTION,
        name: <FormattedMessage id="onboarding.setUpConnection" />,
        // don't navigate by steps for now
        // onSelect:
        //   hasSources && hasDestinations
        //     ? () => updateStep(StepType.SET_UP_CONNECTION)
        //     : undefined
      },
      {
        id: StepType.FINAL,
        name: <FormattedMessage id="onboarding.final" />,
      },
    ],
    []
  );

  return {
    steps,
    currentStep,
    setCurrentStep: updateStep,
  };
};

export default useStepsConfig;
