import React, { Suspense } from "react";
import styled from "styled-components";
import { Redirect, Route, Switch } from "react-router-dom";

import { LoadingPage } from "components";
import useRouter from "components/hooks/useRouterHook";
import FormContent from "./components/FormContent";
import News from "./components/News";

import { LoginPage } from "./LoginPage";
import { SignupPage } from "./SignupPage";
import { ResetPasswordPage } from "./ResetPasswordPage";

const Content = styled.div`
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: row;
  background: ${({ theme }) => theme.whiteColor};
`;

const Part = styled.div`
  flex: 1 0 0;
  padding: 20px 36px 39px 46px;
  height: 100%;
`;

const NewsPart = styled(Part)`
  background: ${({ theme }) => theme.beigeColor};
  padding: 36px 97px 39px 64px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
`;

// TODO: fix route paths

const Auth: React.FC = () => {
  const { pathname } = useRouter();

  return (
    <Content>
      <Part>
        <FormContent toLogin={pathname === "/signup"}>
          <Suspense fallback={<LoadingPage />}>
            <Switch>
              <Route path="/login">
                <LoginPage />
              </Route>
              <Route path="/signup">
                <SignupPage />
              </Route>
              <Route path="/reset-password">
                <ResetPasswordPage />
              </Route>
              <Redirect to="/login" />
            </Switch>
          </Suspense>
        </FormContent>
      </Part>
      <NewsPart>
        <News />
      </NewsPart>
    </Content>
  );
};

export default Auth;
