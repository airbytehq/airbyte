import React, { useMemo, useState, useCallback } from "react";
import { FormattedMessage } from "react-intl";

export enum StepsTypes {
  CREATE_SOURCE = "create-source",
  CREATE_DESTINATION = "create-destination",
  SET_UP_CONNECTION = "set-up-connection"
}

const UseGetStepsConfig = (
  hasSources: boolean,
  hasDestinations: boolean,
  afterUpdateStep?: () => void
) => {
  const getInitialStep = () => {
    if (hasSources) {
      if (hasDestinations) {
        return StepsTypes.SET_UP_CONNECTION;
      }

      return StepsTypes.CREATE_DESTINATION;
    }

    return StepsTypes.CREATE_SOURCE;
  };

  const [currentStep, setCurrentStep] = useState(getInitialStep());
  const updateStep = useCallback(
    (step: StepsTypes) => {
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
        id: StepsTypes.CREATE_SOURCE,
        name: <FormattedMessage id="onboarding.createSource" />,
        onSelect: hasSources
          ? () => updateStep(StepsTypes.CREATE_SOURCE)
          : undefined
      },
      {
        id: StepsTypes.CREATE_DESTINATION,
        name: <FormattedMessage id="onboarding.createDestination" />,
        onSelect:
          hasSources || hasDestinations
            ? () => updateStep(StepsTypes.CREATE_DESTINATION)
            : undefined
      },
      {
        id: StepsTypes.SET_UP_CONNECTION,
        name: <FormattedMessage id="onboarding.setUpConnection" />,
        onSelect:
          hasSources && hasDestinations
            ? () => updateStep(StepsTypes.SET_UP_CONNECTION)
            : undefined
      }
    ],
    [updateStep, hasSources, hasDestinations]
  );

  return {
    steps,
    currentStep,
    setCurrentStep: updateStep
  };
};

export default UseGetStepsConfig;
