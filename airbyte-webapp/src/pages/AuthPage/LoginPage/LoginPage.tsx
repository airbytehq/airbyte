import { Field, FieldProps, Formik } from "formik";
import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import { LabeledInput, LoadingButton, Link } from "components";
import Alert from "components/Alert";
import HeadTitle from "components/HeadTitle";
import { Separator } from "components/Separator";

import { useUser } from "core/AuthContext";
import { IAuthUser } from "core/AuthContext/authenticatedUser";
import { PageTrackingCodes, useTrackPage } from "hooks/services/Analytics";
import { FormHeaderSection } from "pages/AuthPage/components/FormHeaderSection";
import { useAuthenticationService } from "services/auth/AuthSpecificationService";

import styles from "./LoginPage.module.scss";
import { RoutePaths } from "../../routePaths";
import { BottomBlock, FieldItem, Form } from "../components/FormComponents";
import { GoogleAuthBtn } from "../GoogleAuthBtn";

const AuthSeperatorContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const Line = styled.div`
  width: 100%;
  border-top: 1px solid #d6dadf;
`;

const SeperatorText = styled.div`
  font-style: normal;
  font-weight: 400;
  font-size: 12px;
  color: #6b6b6f;
  margin: 0 37px;
`;

const ForgotPasswordContainer = styled.div`
  text-align: right;
  display: none;
`;

const LoginPageValidationSchema = yup.object().shape({
  email: yup.string().email("login.email.error").required("email.empty.error"),
  password: yup.string().required("password.empty.error"),
});

const LoginPage: React.FC = () => {
  const { formatMessage } = useIntl();
  const { user, setUser } = useUser();

  const [errorMessage, setErrorMessage] = useState<string>("");
  const Signin = useAuthenticationService();
  useTrackPage(PageTrackingCodes.LOGIN);

  return (
    <div className={styles.container}>
      <HeadTitle titles={[{ id: "login.pageTitle" }]} />
      <Alert
        message={errorMessage}
        onClose={() => {
          setErrorMessage("");
        }}
      />

      <FormHeaderSection
        link={`/${RoutePaths.Signup}`}
        buttonText={formatMessage({ id: "login.signup" })}
        text={formatMessage({ id: "login.signupDescription" })}
      />
      <div className={styles.formContainer}>
        <img src="/daspireLogo.svg" alt="logo" width={50} style={{ marginTop: "40px" }} />
        <div className={styles.formTitle}>
          <FormattedMessage id="login.title" />
        </div>
        <Formik
          initialValues={{
            email: "",
            password: "",
          }}
          validationSchema={LoginPageValidationSchema}
          onSubmit={async (values) => {
            Signin.post(values, user?.lang)
              .then((res: IAuthUser) => {
                setUser?.(res);
              })
              .catch((err: Error) => {
                setErrorMessage(err.message);
              });
          }}
          validateOnBlur
          validateOnChange
        >
          {({ isValid, dirty, isSubmitting }) => (
            <Form className={styles.form}>
              <GoogleAuthBtn buttonText="signin_with" />
              <Separator height="28px" />
              <AuthSeperatorContainer>
                <Line />
                <SeperatorText>
                  <FormattedMessage id="auth.authSeparator" />
                </SeperatorText>
                <Line />
              </AuthSeperatorContainer>
              <Separator height="40px" />
              <FieldItem bottom="24">
                <Field name="email">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      labelAdditionLength={0}
                      label={<FormattedMessage id="login.yourEmail" />}
                      placeholder={formatMessage({
                        id: "login.yourEmail.placeholder",
                      })}
                      type="text"
                      error={!!meta.error && meta.touched}
                      message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                    />
                  )}
                </Field>
              </FieldItem>
              <FieldItem bottom="24">
                <Field name="password">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      labelAdditionLength={0}
                      label={<FormattedMessage id="login.yourPassword" />}
                      placeholder={formatMessage({
                        id: "login.yourPassword.placeholder",
                      })}
                      type="password"
                      error={!!meta.error && meta.touched}
                      message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                    />
                  )}
                </Field>
              </FieldItem>
              <ForgotPasswordContainer>
                <Link $clear medium to={`/${RoutePaths.ResetPassword}`}>
                  <FormattedMessage id="resetPassword.forgot.title" />
                </Link>
              </ForgotPasswordContainer>
              <BottomBlock>
                <LoadingButton
                  white
                  className={styles.logInBtn}
                  disabled={!(isValid && dirty)}
                  type="submit"
                  isLoading={isSubmitting}
                >
                  <FormattedMessage id="login.button" />
                </LoadingButton>
              </BottomBlock>
            </Form>
          )}
        </Formik>
      </div>
    </div>
  );
};

export default LoginPage;
