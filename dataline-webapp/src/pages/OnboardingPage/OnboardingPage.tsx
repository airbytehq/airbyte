import React, { useMemo, useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import { H2 } from "../../components/Titles";
import StepsMenu from "../../components/StepsMenu";
import SourceStep from "./components/SourceStep";
import DestinationStep from "./components/DestinationStep";
import ConnectionStep from "./components/ConnectionStep";
import useRouter from "../../components/hooks/useRouterHook";
import { Routes } from "../routes";
import SourceResource from "../../core/resources/Source";
import DestinationResource from "../../core/resources/Destination";

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
  const [successRequest, setSuccessRequest] = useState(false);

  const { push } = useRouter();
  const { sources } = useResource(SourceResource.listShape(), {});
  const { destinations } = useResource(DestinationResource.listShape(), {});

  const sourcesDropDownData = useMemo(
    () =>
      sources.map(item => ({
        text: item.name,
        value: item.sourceId,
        img: "/default-logo-catalog.svg"
      })),
    [sources]
  );

  const destinationsDropDownData = useMemo(
    () =>
      destinations.map(item => ({
        text: item.name,
        value: item.destinationId,
        img: "/default-logo-catalog.svg"
      })),
    [destinations]
  );

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

  const onSubmitSourceStep = () => {
    // TODO: action after success request
    setSuccessRequest(true);
    setTimeout(() => {
      setSuccessRequest(false);
      setCurrentStep("create-destination");
    }, 2000);
  };
  const onSubmitDestinationStep = () => {
    // TODO: action after success request
    setSuccessRequest(true);
    setTimeout(() => {
      setSuccessRequest(false);
      setCurrentStep("set-up-connection");
    }, 2000);
  };
  const onSubmitConnectionStep = () => push(Routes.Root);

  const renderStep = () => {
    if (currentStep === "create-source") {
      return (
        <SourceStep
          onSubmit={onSubmitSourceStep}
          dropDownData={sourcesDropDownData}
          hasSuccess={successRequest}
        />
      );
    }
    if (currentStep === "create-destination") {
      return (
        <DestinationStep
          onSubmit={onSubmitDestinationStep}
          dropDownData={destinationsDropDownData}
          hasSuccess={successRequest}
        />
      );
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
        <StepsMenu data={steps} activeStep={currentStep} />
      </StepsCover>
      {renderStep()}
    </Content>
  );
};

export default OnboardingPage;
