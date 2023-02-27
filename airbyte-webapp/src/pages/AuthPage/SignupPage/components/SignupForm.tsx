import { Field, FieldProps, Formik } from "formik";
import React, { useMemo, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import { LabeledInput, Link, LoadingButton } from "components";
import Alert from "components/Alert";
import { Separator } from "components/Separator";

import { useConfig } from "config";
import { useUser } from "core/AuthContext";
import { LOCALES } from "locales";
import { useAuthenticationService } from "services/auth/AuthSpecificationService";

import { BottomBlock, FieldItem, Form, RowFieldItem } from "../../components/FormComponents";
import { GoogleAuthBtn } from "../../GoogleAuthBtn";
import styles from "./SignupForm.module.scss";

interface FormValues {
  firstName: string;
  lastName: string;
  email: string;
  company: string;
  password: string;
  confirmPassword: string;
}

export const FirstNameField: React.FC = () => {
  const { formatMessage } = useIntl();

  return (
    <Field name="firstName">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={<FormattedMessage id="signup.firstName" />}
          placeholder={formatMessage({
            id: "signup.firstName.placeholder",
          })}
          type="text"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

export const LastNameField: React.FC = () => {
  const { formatMessage } = useIntl();

  return (
    <Field name="lastName">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={<FormattedMessage id="signup.lastName" />}
          placeholder={formatMessage({
            id: "signup.lastName.placeholder",
          })}
          type="text"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

export const CompanyNameField: React.FC = () => {
  const { formatMessage } = useIntl();

  return (
    <Field name="company">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={<FormattedMessage id="signup.companyName" />}
          placeholder={formatMessage({
            id: "signup.companyName.placeholder",
          })}
          type="text"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

export const EmailField: React.FC<{ label?: React.ReactNode }> = ({ label }) => {
  const { formatMessage } = useIntl();

  return (
    <Field name="email">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={label || <FormattedMessage id="signup.Email" />}
          placeholder={formatMessage({
            id: "signup.Email.placeholder",
          })}
          type="text"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

export const PasswordField: React.FC<{ label?: React.ReactNode }> = ({ label }) => {
  const { formatMessage } = useIntl();

  return (
    <Field name="password">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={label || <FormattedMessage id="signup.password" />}
          placeholder={formatMessage({
            id: "signup.password.placeholder",
          })}
          type="password"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

export const ConfirmPasswordField: React.FC<{ label?: React.ReactNode }> = ({ label }) => {
  const { formatMessage } = useIntl();

  return (
    <Field name="confirmPassword">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={label || <FormattedMessage id="signup.confirmPassword" />}
          placeholder={formatMessage({
            id: "signup.confirmPassword.placeholder",
          })}
          type="password"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

interface SignupButtonProps {
  isLoading: boolean;
  disabled: boolean;
  buttonMessageId?: string;
}

export const SignupButton: React.FC<SignupButtonProps> = ({
  isLoading,
  disabled,
  buttonMessageId = "signup.submitButton",
}) => (
  <LoadingButton white className={styles.signUpButton} type="submit" isLoading={isLoading} disabled={disabled}>
    <FormattedMessage id={buttonMessageId} />
  </LoadingButton>
);

export const SignupFormStatusMessage: React.FC = ({ children }) => (
  <div className={styles.statusMessage}>{children}</div>
);

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

export const SignupForm: React.FC = () => {
  const [errorMessage, setErrorMessage] = useState<string>("");
  const signUp = useAuthenticationService();
  const { setUser, user } = useUser();

  const validationSchema = useMemo(() => {
    const shape = {
      email: yup.string().email("signup.email.error").required("email.empty.error"),
      password: yup.string().min(8, "signup.password.minLength").required("password.empty.error"),
      firstName: yup.string().min(2, "signup.firstName.minLength").required("firstName.empty.error"),
      lastName: yup.string().min(2, "signup.lastName.minLength").required("lastName.empty.error"),
      company: yup.string().min(2, "signup.companyName.minLength").required("companyName.empty.error"),
      confirmPassword: yup
        .string()
        .oneOf([yup.ref("password"), null], "signup.matchPassword")
        .min(8, `signup.confirmPassword.minLength`)
        .required("confirmPassword.empty.error"),
    };
    return yup.object().shape(shape);
  }, []);

  const config = useConfig();
  return (
    <>
      <Alert
        message={errorMessage}
        onClose={() => {
          setErrorMessage("");
        }}
      />
      <Formik<FormValues>
        initialValues={{
          firstName: "",
          lastName: "",
          email: "",
          company: "",
          password: "",
          confirmPassword: "",
        }}
        validationSchema={validationSchema}
        onSubmit={async (values) => {
          signUp
            .create(values)
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
        {({ isValid, dirty, isSubmitting, status }) => (
          <Form className={styles.form}>
            <GoogleAuthBtn buttonText="signup_with" />
            <Separator height="28px" />
            <AuthSeperatorContainer>
              <Line />
              <SeperatorText>
                <FormattedMessage id="auth.authSeparator" />
              </SeperatorText>
              <Line />
            </AuthSeperatorContainer>
            <Separator height="40px" />
            <RowFieldItem>
              <FirstNameField />
              <LastNameField />
            </RowFieldItem>
            <FieldItem>
              <EmailField />
            </FieldItem>
            <FieldItem>
              <CompanyNameField />
            </FieldItem>
            <FieldItem>
              <PasswordField />
            </FieldItem>
            <FieldItem>
              <ConfirmPasswordField />
            </FieldItem>
            <BottomBlock>
              <SignupButton isLoading={isSubmitting} disabled={!(isValid && dirty)} />
              {status && <SignupFormStatusMessage>{status}</SignupFormStatusMessage>}
            </BottomBlock>
            <div className={styles.termsAndPrivacy}>
              <FormattedMessage
                id="signup.description"
                values={{
                  termLink: (
                    <Link
                      target="_blank"
                      href={user.lang === LOCALES.ENGLISH ? config.links.enTermsLink : config.links.zhTermsLink}
                      as="a"
                      $clear
                    >
                      <FormattedMessage id="signup.terms" />
                    </Link>
                  ),
                  privacyLink: (
                    <Link
                      target="_blank"
                      href={user.lang === LOCALES.ENGLISH ? config.links.enPrivacyLink : config.links.zhPrivacyLink}
                      as="a"
                      $clear
                    >
                      <FormattedMessage id="signup.privacy" />
                    </Link>
                  ),
                }}
              />
            </div>
          </Form>
        )}
      </Formik>
    </>
  );
};
