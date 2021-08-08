import React from "react";
import styled from "styled-components";

import Header from "./Header";

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

const Logo = styled.img`
  margin-bottom: 37px;
  display: block;
`;

const FormContent: React.FC<{ toLogin?: boolean }> = (props) => {
  return (
    <>
      <Header toLogin={props.toLogin} />
      <MainBlock>
        <FormContainer>
          <Logo src="/cloud-main-logo.svg" width={186} />
          {props.children}
        </FormContainer>
      </MainBlock>
    </>
  );
};

export default FormContent;
