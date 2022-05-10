import React, { Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import styled from "styled-components";

import { LoadingPage } from "components";

import useRouter from "hooks/useRouter";
import { CloudRoutes } from "packages/cloud/cloudRoutes";
import { ResetPasswordAction } from "packages/cloud/views/FirebaseActionRoute";

import FormContent from "./components/FormContent";
import News from "./components/News";
import { LoginPage } from "./LoginPage";
import { ResetPasswordPage } from "./ResetPasswordPage";
import { SignupPage } from "./SignupPage";

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
  const { pathname, location } = useRouter();

  return (
    <Content>
      <Part>
        <FormContent toLogin={pathname === `${CloudRoutes.Signup}`}>
          <Suspense fallback={<LoadingPage />}>
            <Routes>
              <Route path={CloudRoutes.Login} element={<LoginPage />} />
              <Route path={CloudRoutes.Signup} element={<SignupPage />} />
              <Route path={CloudRoutes.ResetPassword} element={<ResetPasswordPage />} />
              <Route path={CloudRoutes.FirebaseAction} element={<ResetPasswordAction />} />
              <Route path="*" element={<Navigate to={CloudRoutes.Login} state={{ from: location }} />} />
            </Routes>
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
