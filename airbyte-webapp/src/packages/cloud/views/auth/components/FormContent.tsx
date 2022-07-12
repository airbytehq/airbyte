import React from "react";
import styled from "styled-components";

import { GitBlock } from "./GitBlock";
import { Header } from "./Header";

const MainBlock = styled.div`
  width: 100%;
  height: calc(100% - 100px);
  display: flex;
  align-items: center;
  justify-content: center;
`;

const FormContainer = styled.div`
  max-width: 409px;
  width: 100%;
`;

interface FormContentProps {
  toLogin?: boolean;
  gitBlockVisible?: boolean;
}

const FormContent: React.FC<FormContentProps> = ({ toLogin, children, gitBlockVisible }) => {
  return (
    <>
      <Header toLogin={toLogin} />
      <MainBlock>
        <FormContainer>{children}</FormContainer>
      </MainBlock>
      {gitBlockVisible && <GitBlock />}
    </>
  );
};

export default FormContent;
