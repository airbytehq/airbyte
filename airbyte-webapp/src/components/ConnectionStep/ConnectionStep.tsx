import React, { useState, useEffect } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
// import CreateStepTypes from "components/ConnectionStep";

import useRouter from "hooks/useRouter";

import StepBox from "./components/StepBox";
import CreateStepTypes from "./CreateStepTypes";

export interface StepMenuItem {
  id: string;
  name: string | React.ReactNode;
  status?: string;
  isPartialSuccess?: boolean;
  onSelect?: () => void;
}

interface IProps {
  lightMode?: boolean;
  data?: StepMenuItem[];
  activeStep?: string;
  onSelect?: (id: string) => void;
  type?: "source" | "destination" | "connection";
}

export enum EntityStepsTypes {
  SOURCE = "source",
  DESTINATION = "destination",
  CONNECTION = "connection",
}

export const StepBlock = styled.div`
  width: 100%;
  height: 80px;
  background: #eff0f5;
  font-weight: 500;
  font-size: 16px;
  line-height: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  // margin-bottom: 10px;
`;

export const SingleText = styled.div`
  font-weight: 700;
  font-size: 24px;
  line-height: 30px;
`;

const ConnectionStep: React.FC<IProps> = ({ onSelect, type, lightMode, activeStep }) => {
  const { location } = useRouter();

  const [currentStepNumber, setCurrentStepNumber] = useState<number>(1);

  const connectionStepMenuItem: StepMenuItem[] = [
    {
      id: CreateStepTypes.CREATE_SOURCE,
      name: <FormattedMessage id="onboarding.addSource" />,
    },
    {
      id: CreateStepTypes.CREATE_DESTINATION,
      name: <FormattedMessage id="onboarding.addDestination" />,
    },
    {
      id: CreateStepTypes.CREATE_CONNECTION,
      name: <FormattedMessage id="onboarding.configurations" />,
    },
  ];

  const sourceStepMenuItem: StepMenuItem[] = [
    {
      id: CreateStepTypes.CREATE_SOURCE,
      name: <FormattedMessage id="onboarding.addSource" />,
    },
    {
      id: CreateStepTypes.CREATE_CONNECTION,
      name: <FormattedMessage id="onboarding.configurations" />,
    },
  ];

  const destinationStepMenuItem: StepMenuItem[] = [
    {
      id: CreateStepTypes.CREATE_DESTINATION,
      name: <FormattedMessage id="onboarding.addDestination" />,
    },
    {
      id: CreateStepTypes.CREATE_CONNECTION,
      name: <FormattedMessage id="onboarding.configurations" />,
    },
  ];

  const routes = location.pathname.split("/");
  const locationType = routes[1];

  let steps: StepMenuItem[] = [];
  switch (true) {
    case locationType === "connections":
      steps = connectionStepMenuItem;
      break;
    case locationType === "source":
      steps = destinationStepMenuItem;
      break;
    case locationType === "destination":
      steps = sourceStepMenuItem;
      break;
  }

  // ["", "createSource", "createDestination", "createConnection", "allFinish"];
  const currentStepArray: string[] = steps.map((val) => val.id);
  currentStepArray.push("allFinish");
  currentStepArray.unshift("");

  useEffect(() => {
    if (activeStep !== CreateStepTypes.TEST_CONNECTION) {
      const stepNumber: number = currentStepArray.findIndex((val) => val === activeStep);
      setCurrentStepNumber(stepNumber);
    }
  }, [activeStep, currentStepArray]);

  const StepComponents = () => {
    if (type === "source" || type === "destination") {
      return (
        <SingleText>
          <FormattedMessage id={`${type === "source" ? "onboarding.addSource" : "onboarding.addDestination"}`} />
        </SingleText>
      );
    }
    return (
      <>
        {steps.map((item, key) => (
          <StepBox
            status={item.status}
            isPartialSuccess={item.isPartialSuccess}
            lightMode={lightMode}
            key={item.id}
            stepNumber={key}
            {...item}
            onClick={onSelect || item.onSelect}
            currentStepNumber={currentStepNumber}
            isActive={key < currentStepNumber}
          />
        ))}
      </>
    );
  };

  return <StepBlock>{StepComponents()}</StepBlock>;
};

export default ConnectionStep;
