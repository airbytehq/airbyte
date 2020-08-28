import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

export enum StepsTypes {
  CREATE_SOURCE = "create-source",
  CREATE_DESTINATION = "create-destination",
  SET_UP_CONNECTION = "set-up-connection"
}

const StepsConfig = (hasSources: boolean, hasDestinations: boolean) => {
  const steps = [
    {
      id: StepsTypes.CREATE_SOURCE,
      name: <FormattedMessage id={"onboarding.createSource"} />
    },
    {
      id: StepsTypes.CREATE_DESTINATION,
      name: <FormattedMessage id={"onboarding.createDestination"} />
    },
    {
      id: StepsTypes.SET_UP_CONNECTION,
      name: <FormattedMessage id={"onboarding.setUpConnection"} />
    }
  ];

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

  const nextStep = () => {
    if (currentStep === StepsTypes.CREATE_SOURCE) {
      setCurrentStep(StepsTypes.CREATE_DESTINATION);
    }

    return setCurrentStep(StepsTypes.SET_UP_CONNECTION);
  };

  return {
    steps,
    currentStep,
    nextStep
  };
};

export default StepsConfig;
