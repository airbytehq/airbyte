import { useMemo, useState, useCallback } from "react";
import { FormattedMessage } from "react-intl";

export enum StepsTypes {
  CREATE_SOURCE = "create-source",
  CREATE_DESTINATION = "create-destination",
  SET_UP_CONNECTION = "set-up-connection",
}

const UseGetStepsConfig = (
  hasSources: boolean,
  hasDestinations: boolean,
  afterUpdateStep?: () => void
): {
  currentStep: StepsTypes;
  setCurrentStep: (step: StepsTypes) => void;
  steps: { name: JSX.Element; id: StepsTypes }[];
} => {
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
        // don't navigate by steps for now
        // onSelect: hasSources
        //   ? () => updateStep(StepsTypes.CREATE_SOURCE)
        //   : undefined
      },
      {
        id: StepsTypes.CREATE_DESTINATION,
        name: <FormattedMessage id="onboarding.createDestination" />,
        // don't navigate by steps for now
        // onSelect:
        //   hasSources || hasDestinations
        //     ? () => updateStep(StepsTypes.CREATE_DESTINATION)
        //     : undefined
      },
      {
        id: StepsTypes.SET_UP_CONNECTION,
        name: <FormattedMessage id="onboarding.setUpConnection" />,
        // don't navigate by steps for now
        // onSelect:
        //   hasSources && hasDestinations
        //     ? () => updateStep(StepsTypes.SET_UP_CONNECTION)
        //     : undefined
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

export default UseGetStepsConfig;
