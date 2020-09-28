import React, { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";

export enum StepsTypes {
  CREATE_SOURCE = "create-source",
  CREATE_DESTINATION = "create-destination",
  SET_UP_CONNECTION = "set-up-connection"
}

const StepsConfig = (hasSources: boolean, hasDestinations: boolean) => {
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

  const steps = useMemo(
    () => [
      {
        id: StepsTypes.CREATE_SOURCE,
        name: <FormattedMessage id={"onboarding.createSource"} />,
        onSelect: hasSources
          ? () => setCurrentStep(StepsTypes.CREATE_SOURCE)
          : undefined
      },
      {
        id: StepsTypes.CREATE_DESTINATION,
        name: <FormattedMessage id={"onboarding.createDestination"} />,
        onSelect:
          hasSources || hasDestinations
            ? () => setCurrentStep(StepsTypes.CREATE_DESTINATION)
            : undefined
      },
      {
        id: StepsTypes.SET_UP_CONNECTION,
        name: <FormattedMessage id={"onboarding.setUpConnection"} />,
        onSelect:
          hasSources && hasDestinations
            ? () => setCurrentStep(StepsTypes.SET_UP_CONNECTION)
            : undefined
      }
    ],
    [hasSources, hasDestinations]
  );

  return {
    steps,
    currentStep,
    setCurrentStep
  };
};

export default StepsConfig;
