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
import { Routes } from "packages/cloud/routes";

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

const Auth: React.FC = () => {
  const { pathname } = useRouter();

  return (
    <Content>
      <Part>
        <FormContent toLogin={pathname === Routes.Signup}>
          <Suspense fallback={<LoadingPage />}>
            <Switch>
              <Route path={Routes.Login}>
                <LoginPage />
              </Route>
              <Route path={Routes.Signup}>
                <SignupPage />
              </Route>
              <Route path={Routes.ResetPassword}>
                <ResetPasswordPage />
              </Route>
              <Redirect to={Routes.Login} />
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
