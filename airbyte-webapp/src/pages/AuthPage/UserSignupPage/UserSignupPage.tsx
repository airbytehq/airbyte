import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import HeadTitle from "components/HeadTitle";
import { Separator } from "components/Separator";

import { SignupForm } from "./components/SignupForm";

const Container = styled.div`
  width: 100%;
  height: 100%;
  background-color: #ffffff;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;

const FormContainer = styled.div`
  width: 580px;
  // background-color: red;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const Logo = styled.img`
  max-width: 60px;
  height: auto;
`;

const FormHeading = styled.div`
  font-weight: 700;
  font-size: 30px;
  color: ${({ theme }) => theme.black300};
`;

const UserSignupPage: React.FC = () => {
  return (
    <Container>
      <HeadTitle titles={[{ id: "user.signupPage.title" }]} />
      <FormContainer>
        <Separator height="71px" />
        <Logo src="/daspireLogo.svg" alt="logo" />
        <Separator height="42px" />
        <FormHeading>
          <FormattedMessage id="user.signupPage.heading" />
        </FormHeading>
        <SignupForm />
      </FormContainer>
    </Container>
  );
};

export default UserSignupPage;
