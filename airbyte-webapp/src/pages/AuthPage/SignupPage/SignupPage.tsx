import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import HeadTitle from "components/HeadTitle";

import { PageTrackingCodes, useTrackPage } from "hooks/services/Analytics";

import { Link } from "../../../components/Link";
import { RoutePaths } from "../../routePaths";
import { SignupForm } from "./components/SignupForm";

interface SignupPageProps {
  highlightStyle?: React.CSSProperties;
}

const Container = styled.div`
  display: flex;
  flex-direction: row;
  width: 100%;
  min-height: 100vh;
  background-color: #ffffff;
`;

const InformationContent = styled.div`
  width: 40%;
  // height: 100%;
  background: linear-gradient(75.03deg, #313e6a 1.54%, #0e1331 100%);
  position: relative;
`;

const ImageContent = styled.div`
  position: absolute;
  top: 200px;
  left: 70px;
`;

const LogoHeader = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  padding: 30px;
`;

const LogoText = styled.div`
  font-weight: bold;
  font-size: 16px;
  color: white;
  padding-left: 10px;
`;

const Context = styled.div`
  padding-left: 70px;
  padding-right: 70px;
  margin-top: 10px;
`;

const TitleContent = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const TitleText = styled.div`
  font-weight: bold;
  font-size: 24px;
  color: white;
`;

const FirstListItem = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  padding-top: 50px;
`;

const Text = styled.div`
  font-weight: normal;
  color: white;
  padding-left: 15px;
`;

const ListItem = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  padding-top: 30px;
`;

const FormContent = styled.div`
  width: 60%;
  // height: 100%;
  // background-color: #ffffff;
  background-color: #eff0f5;
`;

const SigninButtonContent = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;
  padding-top: 25px;
  padding-right: 25px;
`;

const SigninText = styled.div`
  font-style: normal;
  font-weight: 400;
  font-size: 14px;
  line-height: 30px;
  color: #6b6b6f;
  padding-right: 10px;
`;

const SigninButton = styled.button`
  background-color: #ffffff;
  padding: 5px 10px;
  font-style: normal;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  color: #4f46e5;
  border-radius: 5px;
  border: 1px solid #4f46e5;
`;

const SignupFormContainer = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: center;
  width: 100%;
`;

const SignupPage: React.FC<SignupPageProps> = () => {
  useTrackPage(PageTrackingCodes.SIGNUP);
  return (
    <Container>
      <HeadTitle titles={[{ id: "signup.pageTitle" }]} />
      <InformationContent>
        <ImageContent>
          <img src="/SignupCover.png" alt="cover" style={{ maxWidth: "80%", height: "auto", objectFit: "cover" }} />
        </ImageContent>
        <LogoHeader>
          <img src="/daspireWhiteLogo.svg" alt="logo" width={40} />
          <LogoText>
            <FormattedMessage id="daspire" />
          </LogoText>
        </LogoHeader>
        <Context>
          <TitleContent>
            <TitleText>
              <FormattedMessage id="signup.Title" />
            </TitleText>
          </TitleContent>
          <FirstListItem>
            <img src="/daspireList1.svg" alt="logo" width={20} />
            <Text>
              <FormattedMessage id="signup.List1" />
            </Text>
          </FirstListItem>

          <ListItem>
            <img src="/daspireList2.svg" alt="logo" width={20} />
            <Text>
              <FormattedMessage id="signup.List2" />
            </Text>
          </ListItem>

          <ListItem>
            <img src="/daspireList6.svg" alt="logo" width={20} />
            <Text>
              <FormattedMessage id="signup.List6" />
            </Text>
          </ListItem>

          <ListItem>
            <img src="/daspireList3.svg" alt="logo" width={20} />
            <Text>
              <FormattedMessage id="signup.List3" />
            </Text>
          </ListItem>

          <ListItem>
            <img src="/daspireList4.svg" alt="logo" width={20} />
            <Text>
              <FormattedMessage id="signup.List4" />
            </Text>
          </ListItem>

          <ListItem>
            <img src="/daspireList5.svg" alt="logo" width={20} />
            <Text>
              <FormattedMessage id="signup.List5" />
            </Text>
          </ListItem>
        </Context>
      </InformationContent>
      <FormContent>
        <SigninButtonContent>
          <SigninText>
            <FormattedMessage id="signup.haveAccount" />
          </SigninText>
          <SigninButton>
            <Link $clear to={`/${RoutePaths.Signin}`}>
              <FormattedMessage id="signup.siginButton" />
            </Link>
          </SigninButton>
        </SigninButtonContent>
        <SignupFormContainer>
          <SignupForm />
        </SignupFormContainer>
      </FormContent>
    </Container>
  );
};

export default SignupPage;
