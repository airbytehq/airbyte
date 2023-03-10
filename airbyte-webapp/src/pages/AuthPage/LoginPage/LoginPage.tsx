import { Field, FieldProps, Formik } from "formik";
import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import { LabeledInput, Link, LoadingButton } from "components";
import Alert from "components/Alert";
import HeadTitle from "components/HeadTitle";
import { Separator } from "components/Separator";

import { useUser } from "core/AuthContext";
import { PageTrackingCodes, useTrackPage } from "hooks/services/Analytics";
import { BottomBlock, FieldItem, Form } from "packages/cloud/views/auth/components/FormComponents";
import { useAuthenticationService } from "services/auth/AuthSpecificationService";

import { RoutePaths } from "../../routePaths";
import { GoogleAuthBtn } from "../GoogleAuthBtn";
import styles from "./LoginPage.module.scss";

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

const LoginPageValidationSchema = yup.object().shape({
  email: yup.string().email("login.email.error").required("email.empty.error"),
  password: yup.string().required("password.empty.error"),
});

const LoginPage: React.FC = () => {
  const [errorMessage, setErrorMessage] = useState<string>("");
  const { formatMessage } = useIntl();
  const { setUser } = useUser();
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
      <img src="/daspireLogo.svg" alt="logo" width={50} />
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
          Signin.post(values)
            .then((res: any) => {
              setUser?.(res);
            })
            .catch((err: any) => {
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
            <FieldItem>
              <Field name="email">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    grey
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
            <FieldItem>
              <Field name="password">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    grey
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
            <div className={styles.signupLink}>
              <FormattedMessage
                id="login.signupDescription"
                values={{
                  signupLink: (
                    <Link to={`/${RoutePaths.Signup}`} $clear>
                      <FormattedMessage id="login.signup" />
                    </Link>
                  ),
                }}
              />
            </div>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default LoginPage;
