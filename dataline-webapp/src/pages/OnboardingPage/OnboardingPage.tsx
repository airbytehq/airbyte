import React, { useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { H2 } from "../../components/Titles";
import StepsMenu from "../../components/StepsMenu";
import SourceStep from "./components/SourceStep";
import DestinationStep from "./components/DestinationStep";
import ConnectionStep from "./components/ConnectionStep";
import useRouter from "../../components/hooks/useRouterHook";
import { Routes } from "../routes";

const Content = styled.div`
  width: 100%;
  max-width: 638px;
  margin: 0 auto;
  padding: 33px 0;
`;

const Img = styled.img`
  text-align: center;
  width: 100%;
`;

const MainTitle = styled(H2)`
  margin-top: -39px;
  font-family: ${({ theme }) => theme.highlightFont};
  color: ${({ theme }) => theme.darkPrimaryColor};
  letter-spacing: 0.008em;
  font-weight: bold;
`;

const Subtitle = styled.div`
  font-size: 14px;
  line-height: 21px;
  color: ${({ theme }) => theme.greyColor40};
  text-align: center;
  margin-top: 7px;
`;

const StepsCover = styled.div`
  margin: 33px 0 28px;
`;

const OnboardingPage: React.FC = () => {
  const { push } = useRouter();

  const steps = [
    {
      id: "create-source",
      name: <FormattedMessage id={"onboarding.createSource"} />
    },
    {
      id: "create-destination",
      name: <FormattedMessage id={"onboarding.createDestination"} />
    },
    {
      id: "set-up-connection",
      name: <FormattedMessage id={"onboarding.setUpConnection"} />
    }
  ];
  const [currentStep, setCurrentStep] = useState("create-source");

  const onSelectStep = (id: string) => setCurrentStep(id);
  const onSubmitSourceStep = () => setCurrentStep("create-destination");
  const onSubmitDestinationStep = () => setCurrentStep("set-up-connection");
  const onSubmitConnectionStep = () => push(Routes.Root);

  const renderStep = () => {
    if (currentStep === "create-source") {
      return <SourceStep onSubmit={onSubmitSourceStep} />;
    }
    if (currentStep === "create-destination") {
      return <DestinationStep onSubmit={onSubmitDestinationStep} />;
    }

    return <ConnectionStep onSubmit={onSubmitConnectionStep} />;
  };

  return (
    <Content>
      <Img src="/welcome.svg" height={132} />
      <MainTitle center>
        <FormattedMessage id={"onboarding.title"} />
      </MainTitle>
      <Subtitle>
        <FormattedMessage id={"onboarding.subtitle"} />
      </Subtitle>
      <StepsCover>
        <StepsMenu
          data={steps}
          onSelect={onSelectStep}
          activeStep={currentStep}
        />
      </StepsCover>
      {renderStep()}
    </Content>
  );
};

export default OnboardingPage;
