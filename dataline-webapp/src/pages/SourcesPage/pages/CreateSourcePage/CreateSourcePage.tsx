import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import PageTitle from "../../../../components/PageTitle";
import StepsMenu from "../../../../components/StepsMenu";
import SourceStep from "./components/SourceStep";
import ConnectionStep from "./components/ConnectionStep";
import { Routes } from "../../../routes";
import useRouter from "../../../../components/hooks/useRouterHook";

const Content = styled.div`
  max-width: 638px;
  margin: 13px auto;
`;

const CreateSourcePage: React.FC = () => {
  const { push } = useRouter();

  const steps = [
    {
      id: "select-source",
      name: <FormattedMessage id={"sources.selectSource"} />
    },
    {
      id: "set-up-connection",
      name: <FormattedMessage id={"onboarding.setUpConnection"} />
    }
  ];
  const [currentStep, setCurrentStep] = useState("select-source");

  const onSelectStep = (id: string) => setCurrentStep(id);
  const onSubmitSourceStep = () => setCurrentStep("set-up-connection");
  const onSubmitConnectionStep = () => push(Routes.Root);

  const renderStep = () => {
    if (currentStep === "select-source") {
      return <SourceStep onSubmit={onSubmitSourceStep} />;
    }

    return <ConnectionStep onSubmit={onSubmitConnectionStep} />;
  };

  return (
    <>
      <PageTitle
        withLine
        title={<FormattedMessage id="sources.newSourceTitle" />}
        middleComponent={
          <StepsMenu
            data={steps}
            onSelect={onSelectStep}
            activeStep={currentStep}
          />
        }
      />
      <Content>{renderStep()}</Content>
    </>
  );
};

export default CreateSourcePage;
