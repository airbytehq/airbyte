import React, { Suspense } from "react";
import styled from "styled-components";
import { Navigate, Route, Routes } from "react-router-dom";

import { LoadingPage } from "components";
import useRouter from "hooks/useRouter";
import FormContent from "./components/FormContent";
import News from "./components/News";

import { CloudRoutes } from "packages/cloud/cloudRoutes";

import { LoginPage } from "./LoginPage";
import { SignupPage } from "./SignupPage";
import { ResetPasswordPage } from "./ResetPasswordPage";
import { ResetPasswordAction } from "packages/cloud/views/FirebaseActionRoute";

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
    <Routes>
      <Route>
        <Content>
          <Part>
            <FormContent toLogin={pathname === CloudRoutes.Signup}>
              <Suspense fallback={<LoadingPage />}>
                <Routes>
                  <Route path={CloudRoutes.Login}>
                    <LoginPage />
                  </Route>
                  <Route path={CloudRoutes.Signup}>
                    <SignupPage />
                  </Route>
                  <Route path={CloudRoutes.ResetPassword}>
                    <ResetPasswordPage />
                  </Route>
                  <Route path={CloudRoutes.FirebaseAction}>
                    <ResetPasswordAction />
                  </Route>
                  <Navigate to={CloudRoutes.Login} />
                </Routes>
              </Suspense>
            </FormContent>
          </Part>
          <NewsPart>
            <News />
          </NewsPart>
        </Content>
      </Route>
    </Routes>
  );
};

export default Auth;
