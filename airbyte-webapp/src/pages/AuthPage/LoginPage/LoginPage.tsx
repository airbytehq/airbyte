import { Field, FieldProps, Formik } from "formik";
import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { LabeledInput, Link, LoadingButton } from "components";
import Alert from "components/Alert";
import HeadTitle from "components/HeadTitle";

import { useUser } from "core/AuthContext";
import { PageTrackingCodes, useTrackPage } from "hooks/services/Analytics";
// import useRouter from "hooks/useRouter";
// import { CloudRoutes } from "packages/cloud/cloudRoutes";
// import { FieldError } from "packages/cloud/lib/errors/FieldError";
// import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { BottomBlock, FieldItem, Form } from "packages/cloud/views/auth/components/FormComponents";
// import { FormTitle } from "packages/cloud/views/auth/components/FormTitle";

// import { OAuthLogin } from "../OAuthLogin";
// import { Disclaimer } from "../SignupPage/components/SignupForm";
import { useAuthenticationService } from "services/auth/AuthSpecificationService";

import { RoutePaths } from "../../routePaths";
import styles from "./LoginPage.module.scss";
// import {CloudRoutes} from "../../../packages/cloud/cloudRoutes";
// import {Simulate} from "react-dom/test-utils";
// import submit = Simulate.submit;

const LoginPageValidationSchema = yup.object().shape({
  email: yup.string().email("login.email.error").required("email.empty.error"),
  password: yup.string().required("password.empty.error"),
});

const LoginPage: React.FC = () => {
  const [errorMessage, setErrorMessage] = useState<string>("");
  const { formatMessage } = useIntl();
  const { setUser } = useUser();
  // const { login } = useAuthService();
  // const { query, replace } = useRouter();
  const Signin = useAuthenticationService();
  useTrackPage(PageTrackingCodes.LOGIN);

  return (
    <div className={styles.container}>
      <HeadTitle titles={[{ title: "Sign In" }]} />
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
            <FieldItem>
              <Field name="email">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
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
              <FormattedMessage id="login.signupDescription" />
              <Link to={`/${RoutePaths.Signup}`} className={styles.link}>
                <FormattedMessage id="login.signup" />
              </Link>
              <FormattedMessage id="login.here" />
            </div>
          </Form>
        )}
      </Formik>

      {/* <OAuthLogin />*/}
      {/* <Disclaimer />*/}
    </div>
  );
};

export default LoginPage;
