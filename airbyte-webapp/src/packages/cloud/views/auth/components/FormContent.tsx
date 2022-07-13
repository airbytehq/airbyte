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

const FormContent: React.FC<{ toLogin?: boolean }> = (props) => {
  return (
    <>
      <Header toLogin={props.toLogin} />
      <MainBlock>
        <FormContainer>{props.children}</FormContainer>
      </MainBlock>
      <GitBlock />
    </>
  );
};

export default FormContent;
