import React from "react";
import styled from "styled-components";

import { useExperiment } from "hooks/services/Experiment";

import { GitBlock } from "./GitBlock";
import { Header } from "./Header";

const MainBlock = styled.div`
  width: 100%;
  display: flex;
  flex: 1 0 auto;
  align-items: center;
  justify-content: center;
`;

const FormContainer = styled.div`
  max-width: 409px;
  width: 100%;
`;

interface FormContentProps {
  toLogin?: boolean;
}

const FormContent: React.FC<React.PropsWithChildren<FormContentProps>> = ({ toLogin, children }) => {
  const hideSelfHostedCTA = useExperiment("authPage.hideSelfHostedCTA", false);

  return (
    <>
      <Header toLogin={toLogin} />
      <MainBlock>
        <FormContainer>{children}</FormContainer>
      </MainBlock>
      {!hideSelfHostedCTA && <GitBlock />}
    </>
  );
};

export default FormContent;
