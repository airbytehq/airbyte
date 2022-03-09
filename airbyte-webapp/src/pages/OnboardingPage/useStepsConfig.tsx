import { useMemo, useState, useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { StepType } from "./types";

const useStepsConfig = (
  hasSources: boolean,
  hasDestinations: boolean,
  hasConnections: boolean,
  afterUpdateStep?: () => void
): {
  currentStep: StepType;
  setCurrentStep: (step: StepType) => void;
  steps: { name: JSX.Element; id: StepType }[];
} => {
  const getInitialStep = () => {
    if (hasSources) {
      if (hasDestinations) {
        if (hasConnections) {
          return StepType.FINAl;
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
      if (afterUpdateStep) {
        afterUpdateStep();
      }
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
        id: StepType.FINAl,
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
