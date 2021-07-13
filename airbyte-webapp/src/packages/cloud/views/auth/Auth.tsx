import React, { Suspense } from "react";
import styled from "styled-components";
import { Redirect, Route, Switch } from "react-router-dom";

import LoadingPage from "components/LoadingPage";
import FormContent from "./components/FormContent";
import { LoginPage } from "./LoginPage";
import { SignupPage } from "./SignupPage";
import useRouter from "components/hooks/useRouterHook";

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
              <Route path={"/login"}>
                <LoginPage />
              </Route>
              <Route path={"/signup"}>
                <SignupPage />
              </Route>
              <Route path={"/reset-password"}>RESET</Route>
              <Redirect to={"/login"} />
            </Switch>
          </Suspense>
        </FormContent>
      </Part>
      <NewsPart />
    </Content>
  );
};

export default Auth;
