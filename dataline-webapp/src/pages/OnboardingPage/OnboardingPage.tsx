import React, { useMemo, useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { useResource, useFetcher } from "rest-hooks";

import { H2 } from "../../components/Titles";
import StepsMenu from "../../components/StepsMenu";
import SourceStep from "./components/SourceStep";
import DestinationStep from "./components/DestinationStep";
import ConnectionStep from "./components/ConnectionStep";
import useRouter from "../../components/hooks/useRouterHook";
import { Routes } from "../routes";
import SourceResource from "../../core/resources/Source";
import DestinationResource from "../../core/resources/Destination";
import SourceImplementationResource from "../../core/resources/SourceImplementation";
import config from "../../config";

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
  const sourcesImplementation = useResource(
    SourceImplementationResource.listShape(),
    {
      workspaceId: config.ui.workspaceId
    }
  );
  const createSourcesImplementation = useFetcher(
    SourceImplementationResource.createShape()
  );

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

  const initialStep = sourcesImplementation.sources.length
    ? "create-destination"
    : "create-source";
  const [currentStep, setCurrentStep] = useState(initialStep);

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    specificationId?: string;
  }) => {
    const result = await createSourcesImplementation(
      {},
      {
        workspaceId: config.ui.workspaceId,
        sourceSpecificationId: values.specificationId,
        connectionConfiguration: {}
      },
      []
    );
    console.log(result);
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
          errorMessage={""}
        />
      );
    }
    if (currentStep === "create-destination") {
      return (
        <DestinationStep
          onSubmit={onSubmitDestinationStep}
          dropDownData={destinationsDropDownData}
          hasSuccess={successRequest}
          errorMessage={""}
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
